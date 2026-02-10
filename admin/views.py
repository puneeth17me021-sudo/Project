from datetime import date

from django.contrib.auth import authenticate, login
from django.db.models import Count, Max, Prefetch
from django.shortcuts import get_object_or_404, redirect, render

from .models import AttendanceRecord, Course, CourseCategory, CourseEnrollment, Lesson


def _student_guard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.groups.filter(name='Student').exists():
        return None
    if request.user.is_staff or request.user.is_superuser:
        return redirect('/admin/')
    if request.user.groups.filter(name='Faculty').exists():
        return redirect('faculty_dashboard')
    return redirect('login')


def _faculty_guard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.groups.filter(name='Faculty').exists():
        return None
    if request.user.is_staff or request.user.is_superuser:
        return redirect('/admin/')
    if request.user.groups.filter(name='Student').exists():
        return redirect('student_dashboard')
    return redirect('login')


def _mark_attendance(student, course, source='enter'):
    AttendanceRecord.objects.get_or_create(
        student=student,
        course=course,
        attendance_date=date.today(),
        defaults={'source': source},
    )


def _resolve_category(existing_category_id, new_category_name):
    if new_category_name:
        name = new_category_name.strip()
        if name:
            category = CourseCategory.objects.filter(name__iexact=name).first()
            if category:
                return category
            return CourseCategory.objects.create(name=name)
    if existing_category_id:
        return CourseCategory.objects.filter(id=existing_category_id).first()
    return None


def home(request):
    return render(request, 'Home Page/front.html')


def about(request):
    return render(request, 'Home Page/about.html')


def course(request):
    return render(request, 'Home Page/course.html')


def contact(request):
    return render(request, 'Home Page/contact.html')


def testimonials(request):
    return render(request, 'Home Page/test.html')


def bastion(request):
    return render(request, 'Home Page/bastion.html')


def privacy(request):
    return render(request, 'Home Page/privacy.html')


def terms(request):
    return render(request, 'Home Page/terms.html')


def index(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        if role == 'admin':
            return redirect('/admin/login/?next=/admin/')
        if role in {'faculty', 'student'}:
            request.session['selected_role'] = role
            return redirect('login')
    return render(request, 'login/index.html')


def login_page(request):
    selected_role = request.session.get('selected_role')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if not user:
            return render(
                request,
                'login/login.html',
                {'error': 'Invalid username or password.', 'selected_role': selected_role},
            )

        is_faculty = user.groups.filter(name='Faculty').exists()
        is_student = user.groups.filter(name='Student').exists()

        if selected_role == 'faculty' and not is_faculty:
            return render(
                request,
                'login/login.html',
                {'error': 'This account is not a faculty account.', 'selected_role': selected_role},
            )

        if selected_role == 'student' and not is_student:
            return render(
                request,
                'login/login.html',
                {'error': 'This account is not a student account.', 'selected_role': selected_role},
            )

        login(request, user)

        if user.is_staff or user.is_superuser:
            return redirect('/admin/')
        if is_faculty:
            return redirect('faculty_dashboard')
        if is_student:
            return redirect('student_dashboard')

        return render(
            request,
            'login/login.html',
            {'error': 'No role assigned to this account.', 'selected_role': selected_role},
        )

    return render(request, 'login/login.html')


def forget_password(request):
    return render(request, 'login/forgetpass.html')


def admin_dashboard(request):
    return render(request, 'login/admin.html')


def faculty_dashboard(request):
    guard = _faculty_guard(request)
    if guard:
        return guard
    context = {
        'category_count': CourseCategory.objects.count(),
        'course_count': Course.objects.count(),
        'lesson_count': Lesson.objects.count(),
        'enrollment_count': CourseEnrollment.objects.count(),
    }
    return render(request, 'FacultyDashboard/courses-dashboard.html', context)


def faculty_courses(request):
    guard = _faculty_guard(request)
    if guard:
        return guard

    courses_qs = Course.objects.filter(is_active=True).annotate(
        enrollment_count=Count('enrollments', distinct=True),
        attendance_count=Count('attendance_records', distinct=True),
        lesson_count=Count('lessons', distinct=True),
    ).order_by('title')
    categories = CourseCategory.objects.prefetch_related(Prefetch('courses', queryset=courses_qs))
    return render(request, 'FacultyDashboard/courses-available.html', {'categories': categories})


def faculty_web_course(request):
    guard = _faculty_guard(request)
    if guard:
        return guard
    return render(request, 'FacultyDashboard/web-development-course.html')


def faculty_python_course(request):
    guard = _faculty_guard(request)
    if guard:
        return guard
    return render(request, 'FacultyDashboard/python-course.html')


def faculty_data_course(request):
    guard = _faculty_guard(request)
    if guard:
        return guard
    return render(request, 'FacultyDashboard/data-analysis-course.html')


def faculty_course_modules(request):
    guard = _faculty_guard(request)
    if guard:
        return guard
    return render(request, 'FacultyDashboard/course-modules.html')


def faculty_course_creation(request):
    guard = _faculty_guard(request)
    if guard:
        return guard

    message = ''
    error = ''
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        level = request.POST.get('level', 'beginner')
        duration = request.POST.get('duration_hours', '0').strip() or '0'
        category = _resolve_category(
            request.POST.get('category_id'),
            request.POST.get('new_category_name', ''),
        )

        if not title:
            error = 'Course title is required.'
        elif not category:
            error = 'Select a category or create a new one.'
        else:
            course, created = Course.objects.get_or_create(
                title=title,
                category=category,
                defaults={
                    'description': description,
                    'level': level if level in {'beginner', 'intermediate', 'advanced'} else 'beginner',
                    'duration_hours': int(duration) if duration.isdigit() else 0,
                    'created_by': request.user,
                    'is_active': True,
                },
            )
            if created:
                message = f'Course "{course.title}" created under "{category.name}".'
            else:
                error = 'This course already exists in the selected category.'

    context = {
        'categories': CourseCategory.objects.all(),
        'message': message,
        'error': error,
    }
    return render(request, 'FacultyDashboard/course-creation.html', context)


def faculty_lesson_upload(request):
    guard = _faculty_guard(request)
    if guard:
        return guard

    message = ''
    error = ''
    if request.method == 'POST':
        lesson_title = request.POST.get('lesson_title', '').strip()
        course_id = request.POST.get('course_id')
        description = request.POST.get('description', '').strip()
        visibility = request.POST.get('visibility', 'public')
        lesson_file = request.FILES.get('lesson_file')

        course = Course.objects.filter(id=course_id).first() if course_id else None
        if not lesson_title:
            error = 'Lesson title is required.'
        elif not course:
            error = 'Select a valid course.'
        else:
            Lesson.objects.create(
                course=course,
                title=lesson_title,
                description=description,
                lesson_file=lesson_file,
                visibility=visibility if visibility in {'public', 'private', 'draft'} else 'public',
                created_by=request.user,
            )
            message = f'Lesson "{lesson_title}" added under "{course.category.name} > {course.title}".'

    courses = Course.objects.filter(is_active=True).select_related('category').order_by('category__name', 'title')
    recent_lessons = Lesson.objects.select_related('course__category').order_by('-created_at')[:10]
    return render(
        request,
        'FacultyDashboard/lesson-upload.html',
        {'courses': courses, 'recent_lessons': recent_lessons, 'message': message, 'error': error},
    )


def student_dashboard(request):
    guard = _student_guard(request)
    if guard:
        return guard
    return render(request, 'StudentDashBord/student.html')


def student_courses(request):
    guard = _student_guard(request)
    if guard:
        return guard

    notice = request.session.pop('student_notice', '')
    courses_qs = Course.objects.filter(is_active=True).annotate(
        enrollment_count=Count('enrollments', distinct=True),
        lesson_count=Count('lessons', distinct=True),
    ).prefetch_related(
        Prefetch('lessons', queryset=Lesson.objects.filter(visibility='public').order_by('-created_at'))
    ).order_by('title')
    categories = CourseCategory.objects.prefetch_related(Prefetch('courses', queryset=courses_qs))
    enrolled_ids = set(
        CourseEnrollment.objects.filter(student=request.user).values_list('course_id', flat=True)
    )
    context = {
        'categories': categories,
        'enrolled_ids': enrolled_ids,
        'notice': notice,
    }
    return render(request, 'StudentDashBord/courses.html', context)


def student_enroll_course(request, course_id):
    guard = _student_guard(request)
    if guard:
        return guard
    if request.method != 'POST':
        return redirect('student_courses')

    course = get_object_or_404(Course, id=course_id, is_active=True)
    CourseEnrollment.objects.get_or_create(student=request.user, course=course)
    _mark_attendance(request.user, course, source='enroll')
    request.session['student_notice'] = f'Enrolled in "{course.title}" under "{course.category.name}".'
    return redirect('student_courses')


def student_enter_course(request, course_id):
    guard = _student_guard(request)
    if guard:
        return guard

    course = get_object_or_404(Course, id=course_id, is_active=True)
    CourseEnrollment.objects.get_or_create(student=request.user, course=course)
    _mark_attendance(request.user, course, source='enter')
    request.session['student_notice'] = f'Attendance marked for "{course.title}" on {date.today()}.'
    return redirect('student_courses')


def student_python(request):
    guard = _student_guard(request)
    if guard:
        return guard
    return render(request, 'StudentDashBord/python.html')


def student_sql(request):
    guard = _student_guard(request)
    if guard:
        return guard
    return render(request, 'StudentDashBord/sql.html')


def student_html(request):
    guard = _student_guard(request)
    if guard:
        return guard
    return render(request, 'StudentDashBord/html.html')


def student_css(request):
    guard = _student_guard(request)
    if guard:
        return guard
    return render(request, 'StudentDashBord/css.html')


def student_quiz(request):
    guard = _student_guard(request)
    if guard:
        return guard
    return render(request, 'StudentDashBord/quiz.html')


def student_progress(request):
    guard = _student_guard(request)
    if guard:
        return guard
    return render(request, 'StudentDashBord/progress.html')


def student_attendance(request):
    guard = _student_guard(request)
    if guard:
        return guard

    enrollments = CourseEnrollment.objects.filter(student=request.user).select_related('course__category')
    summary = AttendanceRecord.objects.filter(student=request.user).values('course_id').annotate(
        present_days=Count('id'),
        last_attended=Max('attendance_date'),
    )
    summary_map = {row['course_id']: row for row in summary}

    rows = []
    for enrollment in enrollments:
        data = summary_map.get(enrollment.course_id, {})
        rows.append({
            'category': enrollment.course.category.name,
            'course': enrollment.course.title,
            'present_days': data.get('present_days', 0),
            'last_attended': data.get('last_attended'),
        })

    return render(request, 'StudentDashBord/attendance.html', {'rows': rows})

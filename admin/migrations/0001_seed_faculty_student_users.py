from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.db import migrations


def seed_users(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    User = apps.get_model('auth', 'User')

    faculty_group, _ = Group.objects.get_or_create(name='Faculty')
    student_group, _ = Group.objects.get_or_create(name='Student')

    faculty_password = 'Faculty@123'
    student_password = 'Student@123'

    for i in range(1, 4):
        username = f'faculty{i}'
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f'{username}@example.com',
                'first_name': f'Faculty{i}',
                'is_staff': False,
                'is_superuser': False,
            },
        )
        if created or not check_password(faculty_password, user.password):
            user.password = make_password(faculty_password)
            user.save(update_fields=['password'])
        user.groups.add(faculty_group)

    for i in range(1, 4):
        username = f'student{i}'
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f'{username}@example.com',
                'first_name': f'Student{i}',
                'is_staff': False,
                'is_superuser': False,
            },
        )
        if created or not check_password(student_password, user.password):
            user.password = make_password(student_password)
            user.save(update_fields=['password'])
        user.groups.add(student_group)


def reverse_seed_users(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    User.objects.filter(username__in=[
        'faculty1', 'faculty2', 'faculty3',
        'student1', 'student2', 'student3',
    ]).delete()


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(seed_users, reverse_seed_users),
    ]

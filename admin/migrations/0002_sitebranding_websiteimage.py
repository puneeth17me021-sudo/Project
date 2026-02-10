from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custom_admin', '0001_seed_faculty_student_users'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteBranding',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('site_name', models.CharField(default='School Of IT Skills', max_length=120)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='branding/logos/')),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Site Branding',
                'verbose_name_plural': 'Site Branding',
            },
        ),
        migrations.CreateModel(
            name='WebsiteImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120)),
                ('image', models.ImageField(upload_to='website/images/')),
                ('page', models.CharField(choices=[('home', 'Home'), ('about', 'About'), ('course', 'Course'), ('testimonials', 'Testimonials'), ('contact', 'Contact'), ('global', 'Global')], default='global', max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]

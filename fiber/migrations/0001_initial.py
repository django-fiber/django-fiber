from django.db import models, migrations
import fiber.utils.fields
import django.db.models.deletion
import fiber.utils.json


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ContentItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('name', models.CharField(max_length=255, verbose_name='name', blank=True)),
                ('content_markup', fiber.utils.fields.FiberMarkupField(verbose_name='Content')),
                ('content_html', fiber.utils.fields.FiberHTMLField(verbose_name='Content')),
                ('protected', models.BooleanField(default=False, verbose_name='protected')),
                ('metadata', fiber.utils.json.JSONField(null=True, verbose_name='metadata', blank=True)),
                ('template_name', models.CharField(max_length=70, verbose_name='template name', blank=True)),
                ('used_on_pages_data', fiber.utils.json.JSONField(null=True, verbose_name='used on pages', blank=True)),
            ],
            options={
                'verbose_name': 'content item',
                'verbose_name_plural': 'content items',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('file', models.FileField(upload_to=b'uploads/files', max_length=255, verbose_name='file')),
                ('title', models.CharField(max_length=255, verbose_name='title')),
            ],
            options={
                'ordering': ('-updated',),
                'verbose_name': 'file',
                'verbose_name_plural': 'files',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('image', models.ImageField(upload_to=b'uploads/images', max_length=255, verbose_name='image')),
                ('title', models.CharField(max_length=255, verbose_name='title')),
                ('width', models.IntegerField(null=True, verbose_name='width', blank=True)),
                ('height', models.IntegerField(null=True, verbose_name='height', blank=True)),
            ],
            options={
                'ordering': ('-updated',),
                'verbose_name': 'image',
                'verbose_name_plural': 'images',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('meta_description', models.CharField(max_length=255, blank=True)),
                ('meta_keywords', models.CharField(max_length=255, blank=True)),
                ('title', models.CharField(max_length=255, verbose_name='title')),
                ('doc_title', models.CharField(max_length=255, verbose_name='document title', blank=True)),
                ('url', fiber.utils.fields.FiberURLField(max_length=255, blank=True)),
                ('mark_current_regexes', models.TextField(verbose_name='mark current regexes', blank=True)),
                ('template_name', models.CharField(max_length=70, verbose_name='template name', blank=True)),
                ('show_in_menu', models.BooleanField(default=True, verbose_name='show in menu')),
                ('is_public', models.BooleanField(default=True, verbose_name='is public')),
                ('protected', models.BooleanField(default=False, verbose_name='protected')),
                ('metadata', fiber.utils.json.JSONField(null=True, blank=True)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
            ],
            options={
                'ordering': ('tree_id', 'lft'),
                'verbose_name': 'page',
                'verbose_name_plural': 'pages',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PageContentItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('block_name', models.CharField(max_length=255, verbose_name='block name')),
                ('sort', models.IntegerField(null=True, verbose_name='sort', blank=True)),
                ('content_item', models.ForeignKey(related_name='page_content_items', verbose_name='content item', to='fiber.ContentItem', on_delete=django.db.models.deletion.CASCADE)),
                ('page', models.ForeignKey(related_name='page_content_items', verbose_name='page', to='fiber.Page', on_delete=django.db.models.deletion.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='page',
            name='content_items',
            field=models.ManyToManyField(to='fiber.ContentItem', verbose_name='content items', through='fiber.PageContentItem'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='page',
            name='parent',
            field=models.ForeignKey(related_name='subpages', verbose_name='parent', blank=True, to='fiber.Page', null=True, on_delete=django.db.models.deletion.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='page',
            name='redirect_page',
            field=models.ForeignKey(related_name='redirected_pages', on_delete=django.db.models.deletion.SET_NULL, verbose_name='redirect page', blank=True, to='fiber.Page', null=True),
            preserve_default=True,
        ),
    ]

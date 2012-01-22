# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Group'
        db.create_table('groupmanager_group', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('organiser', self.gf('django.db.models.fields.related.ForeignKey')(related_name='organiser', to=orm['auth.User'])),
            ('open_organiser', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('desc', self.gf('django.db.models.fields.CharField')(max_length=400, blank=True)),
            ('start_date', self.gf('django.db.models.fields.DateField')(default=datetime.date(2011, 12, 19))),
            ('notify_emails', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_open', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('groupmanager', ['Group'])

        # Adding M2M table for field participants on 'Group'
        db.create_table('groupmanager_group_participants', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('group', models.ForeignKey(orm['groupmanager.group'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('groupmanager_group_participants', ['group_id', 'user_id'])

        # Adding model 'UserProfile'
        db.create_table('groupmanager_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('about_me', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('facebook_id', self.gf('django.db.models.fields.BigIntegerField')(unique=True, null=True, blank=True)),
            ('access_token', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('facebook_name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('facebook_profile_url', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('website_url', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('blog_url', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=255, null=True, blank=True)),
            ('date_of_birth', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('raw_data', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(related_name='member_profile', unique=True, to=orm['auth.User'])),
            ('timezone', self.gf('django.db.models.fields.CharField')(default='Europe/London', max_length=50, blank=True)),
            ('is_nonsocial', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('groupmanager', ['UserProfile'])

        # Adding model 'Address'
        db.create_table('groupmanager_address', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('resident', self.gf('django.db.models.fields.related.ForeignKey')(related_name='address', to=orm['auth.User'])),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=6)),
            ('flat_number', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('street_line1', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('street_line2', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('county', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('postcode', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
        ))
        db.send_create_signal('groupmanager', ['Address'])


    def backwards(self, orm):
        
        # Deleting model 'Group'
        db.delete_table('groupmanager_group')

        # Removing M2M table for field participants on 'Group'
        db.delete_table('groupmanager_group_participants')

        # Deleting model 'UserProfile'
        db.delete_table('groupmanager_userprofile')

        # Deleting model 'Address'
        db.delete_table('groupmanager_address')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'groupmanager.address': {
            'Meta': {'object_name': 'Address'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'county': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'flat_number': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'postcode': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'resident': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'address'", 'to': "orm['auth.User']"}),
            'street_line1': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'street_line2': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '6'})
        },
        'groupmanager.group': {
            'Meta': {'object_name': 'Group'},
            'desc': ('django.db.models.fields.CharField', [], {'max_length': '400', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_open': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'notify_emails': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'open_organiser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'organiser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'organiser'", 'to': "orm['auth.User']"}),
            'participants': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'participant'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'start_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date(2011, 12, 19)'})
        },
        'groupmanager.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'about_me': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'access_token': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'blog_url': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'date_of_birth': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'facebook_id': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'facebook_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'facebook_profile_url': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'is_nonsocial': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'raw_data': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'timezone': ('django.db.models.fields.CharField', [], {'default': "'Europe/London'", 'max_length': '50', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'member_profile'", 'unique': 'True', 'to': "orm['auth.User']"}),
            'website_url': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        }
    }

    complete_apps = ['groupmanager']

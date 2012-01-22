# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'UserProfile'
        db.delete_table('groupmanager_userprofile')

        # Deleting model 'Address'
        db.delete_table('groupmanager_address')

        # Deleting field 'Group.desc'
        db.delete_column('groupmanager_group', 'desc')

        # Deleting field 'Group.start_date'
        db.delete_column('groupmanager_group', 'start_date')

        # Adding field 'Group.desc_short'
        db.add_column('groupmanager_group', 'desc_short', self.gf('django.db.models.fields.CharField')(default='initial value', max_length=400), keep_default=False)

        # Adding field 'Group.desc_long'
        db.add_column('groupmanager_group', 'desc_long', self.gf('django.db.models.fields.TextField')(default='', blank=True), keep_default=False)

        # Adding field 'Group.created_date'
        db.add_column('groupmanager_group', 'created_date', self.gf('django.db.models.fields.DateField')(default=datetime.date(2011, 12, 21)), keep_default=False)


    def backwards(self, orm):
        
        # Adding model 'UserProfile'
        db.create_table('groupmanager_userprofile', (
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=255, null=True, blank=True)),
            ('about_me', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(related_name='member_profile', unique=True, to=orm['auth.User'])),
            ('timezone', self.gf('django.db.models.fields.CharField')(default='Europe/London', max_length=50, blank=True)),
            ('is_nonsocial', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('access_token', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('raw_data', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('facebook_name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('date_of_birth', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('blog_url', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('facebook_id', self.gf('django.db.models.fields.BigIntegerField')(unique=True, null=True, blank=True)),
            ('facebook_profile_url', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('website_url', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('groupmanager', ['UserProfile'])

        # Adding model 'Address'
        db.create_table('groupmanager_address', (
            ('street_line2', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('street_line1', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('resident', self.gf('django.db.models.fields.related.ForeignKey')(related_name='address', to=orm['auth.User'])),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('county', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('postcode', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=6)),
            ('flat_number', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
        ))
        db.send_create_signal('groupmanager', ['Address'])

        # Adding field 'Group.desc'
        db.add_column('groupmanager_group', 'desc', self.gf('django.db.models.fields.CharField')(default='', max_length=400, blank=True), keep_default=False)

        # Adding field 'Group.start_date'
        db.add_column('groupmanager_group', 'start_date', self.gf('django.db.models.fields.DateField')(default=datetime.date(2011, 12, 19)), keep_default=False)

        # Deleting field 'Group.desc_short'
        db.delete_column('groupmanager_group', 'desc_short')

        # Deleting field 'Group.desc_long'
        db.delete_column('groupmanager_group', 'desc_long')

        # Deleting field 'Group.created_date'
        db.delete_column('groupmanager_group', 'created_date')


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
        'groupmanager.group': {
            'Meta': {'object_name': 'Group'},
            'created_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date(2011, 12, 21)'}),
            'desc_long': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'desc_short': ('django.db.models.fields.CharField', [], {'max_length': '400'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_open': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'notify_emails': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'open_organiser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'organiser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'organiser'", 'to': "orm['auth.User']"}),
            'participants': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'participant'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['groupmanager']

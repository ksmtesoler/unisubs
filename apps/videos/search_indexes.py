from haystack.indexes import *
from haystack import site
from models import Video, SubtitleLanguage
from comments.models import Comment
from auth.models import CustomUser as User
from utils.celery_search_index import CelerySearchIndex

class VideoIndex(CelerySearchIndex):
    text = CharField(document=True, use_template=True)
    title = CharField(model_attr='title_display') 
    languages = MultiValueField()
    video_language = CharField() 
    created = DateTimeField(model_attr='created')
    edited = DateTimeField(model_attr='edited')
    subtitles_fetched_count = IntegerField(model_attr='subtitles_fetched_count')
    widget_views_count = IntegerField(model_attr='widget_views_count')
    comments_count = IntegerField()
    languages_count = IntegerField(model_attr='languages_count')
    contributors_count = IntegerField()
    activity_count = IntegerField()
    
    week_views = IntegerField()
    month_views = IntegerField()
    year_views = IntegerField()
    total_views = IntegerField(model_attr='view_count')
    
    def prepare(self, obj):
        self.prepared_data = super(VideoIndex, self).prepare(obj)
        langs = obj.subtitlelanguage_set.exclude(language=u'')
        self.prepared_data['video_language'] = obj.language and '%s ++++++++++' % obj.language or ''
        self.prepared_data['languages'] = ['%s ++++++++++' % lang.language for lang in langs if lang.latest_subtitles()]
        self.prepared_data['comments_count'] = Comment.get_for_object(obj).count()
        self.prepared_data['contributors_count'] = User.objects.filter(subtitleversion__language__video=obj).distinct().count()
        self.prepared_data['activity_count'] = obj.action_set.count()
        self.prepared_data['week_views'] = obj.views['week']
        self.prepared_data['month_views'] = obj.views['month']
        self.prepared_data['year_views'] = obj.views['year']
        return self.prepared_data

    def _setup_save(self, model):
        pass
    
    def _teardown_save(self, model):
        pass
        
class SubtitleLanguageIndex(CelerySearchIndex):
    text = CharField(document=True, use_template=True)
    title = CharField()
    language = CharField()

    def prepare(self, obj):
        self.prepared_data = super(SubtitleLanguageIndex, self).prepare(obj)
        self.prepared_data['title'] = obj.video.__unicode__()
        self.prepared_data['language'] = obj.language_display()
        return self.prepared_data
    
site.register(Video, VideoIndex)
#site.register(SubtitleLanguage, SubtitleLanguageIndex)

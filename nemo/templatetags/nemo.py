from django import template
from django.conf import settings

#class NemoUriRootNode(template.Node):
#    '''render nemo uri root from settings'''    
#    def render(self, context):
#        return settings.NEMO_URI_ROOT
#    
#    @classmethod
#    def do_tag(cls, parser, token):
#        return cls()
#    
#class ProjectNameNode(template.Node):
#    '''render nemo uri root from settings'''
#    
#    def render(self, context):
#        return settings.PROJECT_NAME.capitalize()
#    
#    @classmethod
#    def do_tag(cls, parser, token):
#        return cls()    

register = template.Library()
#register.tag('nemo_root', NemoUriRootNode.do_tag)
#register.tag('project_name', ProjectNameNode.do_tag)

@register.simple_tag
def nemo_root():
    return settings.NEMO_URI_ROOT

@register.simple_tag
def project_name():
    return settings.PROJECT_NAME.capitalize()
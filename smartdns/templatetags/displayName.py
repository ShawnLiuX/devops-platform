from django import template

register = template.Library()

@register.filter(name='sname_display')
def sname_display(value):
    res = value.get_sname_display
    return res()

#def displayName(value, arg):
#    return apply(eval('value.get_'+arg+'_display'), ())

import pystache
def f(df):
    return "{{jor.a}}"
print pystache.render("{{#list}}{{a}}{{/list}} ", {'list': [{'a': 'b', 'c': 'd'}]})


# coding: utf-8

from django.template import Template, Context

POST_MAIN = '''
<div class="post-header">
  <span class="louzhu"><a name="post{{ post.id }}">{{ post.id }}</a></span>
  <span class="user"><a href="{% url account:show_user post.user.id %}">{{ post.user }}</a></span>
  <span class="time">{{ post.updated|date:"Y年m月d日 H:i" }}</span>
  {% ifequal user post.user %}
  [<span class="delete"><a href="{% url wiki:del_post post.id %}">删除</a></span>]
  {% endifequal %}
  <span><button type="button" onclick="javascript: ajax_new_post(this, 'POST', '{{ post.id }}')">盖楼</button></span>
</div>
<div class="post-body">
  <p>{{ post.body_html|safe }}</p>
</div>
'''


def render_post(post):

    POST_ITERM = '<div class="post-item">\n'

    t = Template(POST_MAIN)
    c = Context({'post': post})
    POST_ITERM += t.render(c)
    if post.children:
        for child in post.children:
            POST_ITERM += render_post(child)

    POST_ITERM += '\n</div>'

    return POST_ITERM

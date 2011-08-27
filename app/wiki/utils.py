# coding: utf-8

from django.template import Template, Context

POST_MAIN = '''
<div class="post-header">
  <span class="louzhu"><a name="post{{ post.id }}">{{ post.id }}</a></span>
  <span class="user"><a href="{% url account:show_user post.user.id %}">{{ post.user }}</a></span>
  <span class="time">{{ post.updated|date:"Y年m月d日 H:i" }}</span>
  {% ifequal user post.user %}
  <!--<span class="post-delete"><a href="{% url wiki:del_post post.id %}">删除</a></span>-->
  <span class="post-edit"><button type="button" onclick="javascript: ajax_edit_post(this, '{{ post.id }}')">编辑</button></span>
  {% endifequal %}
  <span><button type="button" onclick="javascript: ajax_new_post(this, 'POST', '{{ post.id }}')">回复</button></span>
  <span class="right"><a onclick="javascript: scrollTo(0,0);" href="javascript:;">TOP</a></span>
</div>
<div class="post-body">
  <p>{{ post.body_html|safe }}</p>
</div>
'''


def render_post(user, post):

    POST_ITERM = '<div class="post-item box">\n'

    t = Template(POST_MAIN)
    c = Context({'post': post, 'user': user})
    POST_ITERM += t.render(c)
    if post.children:
        for child in post.children:
            POST_ITERM += render_post(user, child)

    POST_ITERM += '\n</div>\n'

    return POST_ITERM

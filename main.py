from flask import Flask

from app import views

app = Flask(__name__)
app.secret_key = "secret key"



app.add_url_rule("/", "home", views.home)
app.add_url_rule('/index', 'index', views.index)
app.add_url_rule('/add_link', 'add_link', views.add_link, methods=['POST'])
app.add_url_rule('/delete_link', 'delete_link', views.delete_link, methods=['POST'])
app.add_url_rule('/modify_link', 'modify_link', views.modify_link, methods=['POST'])
app.add_url_rule("/login", "login", views.login, methods=["GET", "POST"])
app.add_url_rule("/logout", "logout", views.logout)
app.add_url_rule("/video_feed","video_feed",views.video_feed)
app.add_url_rule("/display","display",views.display,methods=["GET","POST"])
app.add_url_rule("/report","report",views.report,methods=["GET","POST"])
app.add_url_rule('/displayimage',"displayimage",views.displayimage,methods=["GET","POST"])
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

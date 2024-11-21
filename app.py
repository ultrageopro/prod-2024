from flask import Flask
import os

from .routes.ping_route import PingRoute
from .routes.country_route import CountryRoute
from .routes.auth.register_route import RegisterRoute
from .routes.auth.sign_in_route import SignInRoute
from .routes.me.profile_route import ProfileRoute
from .routes.profiles_route import ProfilesRoute
from .routes.friends.add_route import AddFriendRoute
from .routes.me.update_password_route import UpdatePasswordRoute
from .routes.friends.remove_route import RemoveFriendRoute
from .routes.friends.list_route import ListFriendRoute
from .routes.posts.posts_routes import PostsRoute


from .database.user_database import UserPostgreClient
from .database.countries_database import CountryPostgreClient
from .database.friend_database import FriendsPostgreClient
from .database.posts_database import PostPostgreClient
from .database.reactions_database import ReactionPostgreClient


app = Flask(__name__)  # create a new Flask app instance

port = os.environ.get(
    "SERVER_PORT"
)  # get the server port from the environment variables


ps_conn = os.environ.get(
    "POSTGRES_CONN"
)  # get the PostgreSQL connection string from the environment variables


user_database = UserPostgreClient(ps_conn)  # create a new user database instance
country_database = CountryPostgreClient(
    ps_conn
)  # create a new country database instance
friend_database = FriendsPostgreClient(
    ps_conn
)  # create a new friend database instances
post_database = PostPostgreClient(ps_conn)  # create a new post database instances
reactions_database = ReactionPostgreClient(
    ps_conn
)  # create a new reactions database instances

ping_route = PingRoute()  # create a new PingRoute instance
country_route = CountryRoute(country_database)  # create a new CountryRoute instance
register_route = RegisterRoute(
    user_database, country_database
)  # create a new RegisterRoute instance
login_route = SignInRoute(user_database)  # create a new LoginRoute instance
profile_route = ProfileRoute(
    user_database, country_database
)  # create a new ProfileRoute instance
profiles_route = ProfilesRoute(user_database)  # create a new ProfilesRoute instance
update_password_route = UpdatePasswordRoute(
    user_database
)  # create a new UpdatePasswordRoute instance
add_friend_route = AddFriendRoute(
    user_database, friend_database
)  # create a new AddFriendRoute instance
remove_friend_route = RemoveFriendRoute(
    user_database, friend_database
)  # create a new RemoveFriendRoute instance
list_friend_route = ListFriendRoute(
    user_database, friend_database
)  # create a new ListFriendRoute instance
new_route = PostsRoute(
    post_database, user_database, friend_database, reactions_database
)  # create a new NewRoute instance


app.register_blueprint(ping_route.blueprint)  # register the ping route blueprint
app.register_blueprint(country_route.blueprint)  # register the country route blueprint
app.register_blueprint(
    register_route.blueprint
)  # register the register route blueprint
app.register_blueprint(login_route.blueprint)  # register the login route blueprint
app.register_blueprint(profile_route.blueprint)  # register the profile route blueprint
app.register_blueprint(
    profiles_route.blueprint
)  # register the profiles route blueprint
app.register_blueprint(
    update_password_route.blueprint
)  # register the update password route blueprint
app.register_blueprint(
    add_friend_route.blueprint
)  # register the add friend route blueprint
app.register_blueprint(
    remove_friend_route.blueprint
)  # register the remove friend route blueprint
app.register_blueprint(
    list_friend_route.blueprint
)  # register the list friend route blueprint
app.register_blueprint(new_route.blueprint)  # register the new route blueprint

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port, threaded=False)  # run the app

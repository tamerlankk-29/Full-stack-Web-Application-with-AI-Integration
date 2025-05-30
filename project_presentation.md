# Project Presentation: Flask Full-Stack Web Application with AI Integration


## Introduction


This project is a full-featured web application blog platform developed using the Flask framework. The application demonstrates the implementation of a modern, secure, and interactive web platform with the integration of artificial intelligence technologies to enhance the user experience.


## 1. Project Description


### User Registration and Login System


The project implements a comprehensive user authentication system:


- **New User Registration**: Users can create accounts by providing a unique username, email, and password.
- **Secure Password Storage**: All passwords are hashed using the werkzeug.security library before being stored in the database.
- **Login System**: A login form with credential verification and session management is implemented.
- **User Profiles**: Users can customize their profiles, including personal information and profile pictures.
- **Password Reset**: A password reset mechanism via email is implemented.


```python
# Example from the User model
def set_password(self, password):
    """Set password hash from plain text password"""
    self.password_hash = generate_password_hash(password)


def check_password(self, password):
    """Check if password matches the hash"""
    return check_password_hash(self.password_hash, password)
```


### Data Interaction through Forms


The project uses Flask-WTF to create and process forms:


- **Registration and Login Forms**: Validation of user data.
- **Post Creation and Editing Forms**: Management of blog content.
- **Comment Forms**: User interaction with content.
- **Search Forms**: Content filtering and search.
- **Profile Management Forms**: Updating personal information and uploading images.


```python
# Example of a post creation form
class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=3, max=120)])
    content = TextAreaField('Content', validators=[DataRequired()])
    tags = StringField('Tags (comma separated)', validators=[Optional()])
    image = FileField('Image', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg', 'gif'])])
    published = BooleanField('Publish', default=True)
    submit = SubmitField('Submit')
```


### CRUD Operations with Database


The project demonstrates a complete set of CRUD (Create, Read, Update, Delete) operations:


- **Create**: Creation of new users, posts, comments, and tags.
- **Read**: Viewing posts, comments, user profiles, and tags.
- **Update**: Editing posts and user profiles.
- **Delete**: Removing posts and comments.


```python
# Example of creating a new post
@posts_bp.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            content=form.content.data,
            user_id=current_user.id,
            published=form.published.data
        )
        # Image and tag processing
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('posts.post', post_id=post.id))
```


### Session Management


Comprehensive user session management is implemented:


- **Session Creation on Login**: A user session is created upon successful authentication.
- **Secure Session Data Storage**: Secure storage with a secret key is used.
- **Session Timeout**: Automatic logout after 30 minutes of inactivity.
- **"Remember Me" Functionality**: Long-term sessions for trusted devices.
- **Last Activity Time Update**: Tracking user activity.


```python
@auth_bp.before_request
def check_session_timeout():
    """Check if user session has timed out"""
    if current_user.is_authenticated:
        last_active = session.get('last_active')
        session['last_active'] = datetime.utcnow().timestamp()
        if last_active and datetime.utcnow().timestamp() - last_active > SESSION_TIMEOUT:
            logout_user()
            flash('Your session has expired. Please login again.', 'info')
            return redirect(url_for('auth.login'))
```


### File Uploads


The project supports secure file upload and management:


- **User Avatar Uploads**: Profile personalization.
- **Post Image Uploads**: Visual enrichment of content.
- **File Type Validation**: Verification of allowed image formats.
- **File Size Limitation**: Prevention of uploading excessively large files.
- **Secure Storage**: Generation of random file names to prevent conflicts.
- **Image Resizing**: Optimization for web display.


```python
def save_picture(form_picture, folder='uploads', size=(800, 800)):
    """Save uploaded picture with a random name and resize it"""
    random_hex = secrets.token_hex(8)
    _, file_ext = os.path.splitext(form_picture.filename)
    picture_filename = random_hex + file_ext
    upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
    os.makedirs(upload_folder, exist_ok=True)
    picture_path = os.path.join(upload_folder, picture_filename)
    img = Image.open(form_picture)
    img.thumbnail(size)
    img.save(picture_path)
    return picture_filename
```


### Object-Oriented Architecture


The project is built using OOP principles:


- **Data Models**: Classes for representing database entities (User, Post, Comment, Tag).
- **Forms**: Classes for processing and validating user input.
- **Blueprints**: Modular organization of routes and views.
- **Utilities**: Helper classes and functions for common operations.
- **Application Factory**: Pattern for creating application instances.


```python
# Example of Post model with relationships
class Post(db.Model):
    """Post model for blog posts or other content"""
    __tablename__ = 'posts'


    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_file = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published = db.Column(db.Boolean, default=True)
   
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
   
    # Relationships
    comments = db.relationship('Comment', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    tags = db.relationship('Tag', secondary=post_tags, backref=db.backref('posts', lazy='dynamic'))
```


### Use of Templates for Rendering Pages


The project uses the Jinja2 template system for dynamic page rendering:


- **Base Template**: Common structure for all pages.
- **Template Inheritance**: Extension of the base template for different page types.
- **Conditional Logic**: Content display based on user state.
- **Loops**: Iteration through data collections (posts, comments, tags).
- **Macros**: Reusable interface components.
- **Filters**: Data formatting for display.


```html
<!-- Example template with conditional logic and loops -->
{% extends "base.html" %}
{% block content %}
    {% if current_user.is_authenticated %}
        <h2>Welcome back, {{ current_user.username }}!</h2>
    {% else %}
        <h2>Welcome to our blog!</h2>
    {% endif %}
   
    <div class="posts">
        {% for post in posts %}
            <div class="post">
                <h3>{{ post.title }}</h3>
                <p>{{ post.content|truncate(200) }}</p>
            </div>
        {% endfor %}
    </div>
{% endblock %}
```


### AI Integration


Two key artificial intelligence functions are integrated into the project:


1. **Comment Sentiment Analysis**:
   - Automatic analysis of the emotional tone of user comments.
   - Classification of comments as positive, negative, or neutral.
   - Visual representation of sentiment using color coding and emojis.


2. **Content Recommendation System**:
   - Content similarity analysis using TF-IDF vectorization.
   - Similar post recommendations based on cosine similarity.
   - Personalized recommendations based on user interaction history.


```python
# Example of comment sentiment analysis
def analyze_sentiment(text):
    """Analyze the sentiment of a text using TextBlob"""
    cleaned_text = clean_text(text)
    blob = TextBlob(cleaned_text)
    polarity = blob.sentiment.polarity
   
    if polarity > 0.1:
        sentiment = 'positive'
    elif polarity < -0.1:
        sentiment = 'negative'
    else:
        sentiment = 'neutral'
   
    return {
        'polarity': polarity,
        'subjectivity': blob.sentiment.subjectivity,
        'sentiment': sentiment
    }
```




## 2. Functional Requirements


### 2.1. Server Requests and Data Handling


The project implements comprehensive HTTP request and data processing:


- **GET and POST Methods**: All forms and data operations use appropriate HTTP methods.
  - GET for retrieving data (viewing posts, profiles, search pages)
  - POST for submitting data (creating posts, comments, updating profiles)


- **Flask Routing**: Structured routing system using Blueprints.
  ```python
  @posts_bp.route('/post/<int:post_id>')
  def post(post_id):
      """View a specific post"""
      post = Post.query.get_or_404(post_id)
      # Access checking and template rendering
  ```


- **Request Processing**: Using various Flask methods for data processing.
  ```python
  # Example of form data processing
  form_data = request.form.get('field_name')
 
  # Example of URL parameter processing
  page = request.args.get('page', 1, type=int)
 
  # Example of uploaded file processing
  file = request.files['profile_picture']
  ```


- **Error Handling**: Proper handling and display of HTTP errors.
  ```python
  @errors_bp.app_errorhandler(404)
  def error_404(error):
      return render_template('errors/404.html'), 404
  ```


### 2.2. Forms and Validation


The project uses WTForms for creating and validating forms:


- **Form Definition**: Structured definition of fields and validators.
  ```python
  class RegistrationForm(FlaskForm):
      username = StringField('Username', validators=[
          DataRequired(),
          Length(min=3, max=64),
          Regexp('^[A-Za-z][A-Za-z0-9_.]*$', message='Usernames must start with a letter and can only contain letters, numbers, dots or underscores')
      ])
      email = EmailField('Email', validators=[DataRequired(), Email()])
      password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
      confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
      submit = SubmitField('Register')
  ```


- **Data Validation**: Checking all input data for compliance with requirements.
  - Required field validation
  - Email validation
  - Password length and format checking
  - Username and email uniqueness validation
  - Uploaded file type and size validation


- **Error Feedback**: Clear user notification about input issues.
  ```html
  {% if form.username.errors %}
      {{ form.username(class="form-control is-invalid") }}
      <div class="invalid-feedback">
          {% for error in form.username.errors %}
              {{ error }}
          {% endfor %}
      </div>
  {% else %}
      {{ form.username(class="form-control") }}
  {% endif %}
  ```


- **Custom Validators**: Additional checks for specific requirements.
  ```python
  def validate_username(self, username):
      user = User.query.filter_by(username=username.data).first()
      if user:
          raise ValidationError('That username is already taken. Please choose a different one.')
  ```


### 2.3. Cookies and Sessions


The project uses Flask cookies and session mechanisms to manage user state:


- **Flask Session Management**: Using Flask-Login for authentication.
  ```python
  login_user(user, remember=form.remember_me.data)
  session['last_active'] = datetime.utcnow().timestamp()
  ```


- **Secure Session Data Storage**: Using a secret key for encryption.
  ```python
  app.config.from_mapping(
      SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
      # Other settings
  )
  ```


- **User Data Storage**: Saving information between requests.
  ```python
  # Saving data in the session
  session['key'] = value
 
  # Retrieving data from the session
  value = session.get('key')
  ```


- **Flash Messages**: Informing users about action results.
  ```python
  flash('Your account has been created! You can now log in.', 'success')
  ```


### 2.4. Advanced Session Management


The project implements advanced session management features:


- **Session Timeout**: Automatic logout on inactivity.
  ```python
  SESSION_TIMEOUT = 30 * 60  # 30 minutes
 
  @auth_bp.before_request
  def check_session_timeout():
      if current_user.is_authenticated:
          last_active = session.get('last_active')
          session['last_active'] = datetime.utcnow().timestamp()
          if last_active and datetime.utcnow().timestamp() - last_active > SESSION_TIMEOUT:
              logout_user()
              flash('Your session has expired. Please login again.', 'info')
              return redirect(url_for('auth.login'))
  ```


- **"Remember Me" Functionality**: Long-term sessions for trusted devices.
  ```python
  # In the login form
  remember_me = BooleanField('Remember Me')
 
  # When logging in a user
  login_user(user, remember=form.remember_me.data)
  ```


- **Last Activity Time Update**: Tracking user actions.
  ```python
  current_user.update_last_seen()
  ```


- **Secure Logout**: Complete removal of session data on logout.
  ```python
  @auth_bp.route('/logout')
  def logout():
      logout_user()
      flash('You have been logged out.', 'info')
      return redirect(url_for('main.home'))
  ```


### 2.5. Database Integration


The project uses SQLAlchemy ORM for database interaction:


- **Model Definition**: Object-oriented representation of tables.
  ```python
  class User(db.Model, UserMixin):
      __tablename__ = 'users'
      id = db.Column(db.Integer, primary_key=True)
      username = db.Column(db.String(64), unique=True, nullable=False, index=True)
      email = db.Column(db.String(120), unique=True, nullable=False, index=True)
      # Other fields
  ```


- **Table Relationships**: Implementation of one-to-many and many-to-many relationships.
  ```python
  # One-to-many relationship
  posts = db.relationship('Post', backref='author', lazy='dynamic', cascade='all, delete-orphan')
 
  # Many-to-many relationship
  post_tags = db.Table('post_tags',
      db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True),
      db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
  )
  ```


- **Database Error Handling**: Proper exception handling.
  ```python
  try:
      db.session.commit()
  except IntegrityError:
      db.session.rollback()
      flash('Error: Username or email already exists.', 'danger')
  ```


- **Schema Migrations**: Ability to update database structure.
  ```python
  # Creating tables
  with app.app_context():
      db.create_all()
  ```


### 2.6. CRUD Operations


The project implements a complete set of CRUD operations for main entities:


- **Create (Creation)**:
  ```python
  # Creating a new post
  post = Post(title=form.title.data, content=form.content.data, user_id=current_user.id)
  db.session.add(post)
  db.session.commit()
  ```


- **Read (Reading)**:
  ```python
  # Getting a single post
  post = Post.query.get_or_404(post_id)
 
  # Getting a list of posts with pagination
  posts = Post.query.order_by(Post.created_at.desc()).paginate(page=page, per_page=5)
  ```


- **Update (Updating)**:
  ```python
  # Updating an existing post
  post.title = form.title.data
  post.content = form.content.data
  db.session.commit()
  ```


- **Delete (Deletion)**:
  ```python
  # Deleting a post
  db.session.delete(post)
  db.session.commit()
  ```


- **Using HTTP Methods**: Adherence to RESTful principles.
  - GET for retrieving data
  - POST for creating new records
  - PUT/POST for updating
  - DELETE/POST for deleting


### 2.7. User Authentication


The project implements a secure authentication system:


- **Password Hashing**: Using werkzeug.security to protect passwords.
  ```python
  # Hashing a password when creating/changing
  self.password_hash = generate_password_hash(password)
 
  # Checking a password when logging in
  check_password_hash(self.password_hash, password)
  ```


- **Session Management**: Using Flask-Login to track users.
  ```python
  # Loading a user
  @login_manager.user_loader
  def load_user(user_id):
      return User.query.get(int(user_id))
  ```


- **Route Protection**: Restricting access for unauthenticated users.
  ```python
  @login_required
  def profile():
      # Code accessible only to authenticated users
  ```


- **Access Rights Checking**: Restricting actions for unauthorized users.
  ```python
  # Checking if the current user is the author of the post
  if post.user_id != current_user.id:
      abort(403)  # Forbidden
  ```


### 2.8. Advanced Database Techniques


The project demonstrates advanced database techniques:


- **Using SQLAlchemy Relationships**: Efficient work with related data.
  ```python
  # Getting all user posts
  user.posts.all()
 
  # Getting the post author
  post.author
  ```


- **Complex Queries**: Using filtering and sorting.
  ```python
  # Searching by title and content
  base_query = Post.query.filter(
      (Post.title.contains(query) | Post.content.contains(query)) &
      Post.published == True
  )
  ```


- **Query Combining**: Combining results from different queries.
  ```python
  # Combining search results from posts and tags
  tag_query = Post.query.join(Post.tags).filter(
      Post.published == True,
      Tag.name.contains(query)
  )
  combined_query = base_query.union(tag_query)
  ```


- **Search Function**: Implementing search with filtering by various criteria.
  ```python
  @main_bp.route('/search')
  def search():
      query = request.args.get('query', '')
      # Search and filtering logic
      return render_template('main/search_results.html', posts=posts, query=query)
  ```


### 2.9. File Uploads


The project supports secure file upload and management:


- **Image Upload Processing**: Support for avatar and post image uploads.
  ```python
  @auth_bp.route('/profile/picture', methods=['POST'])
  @login_required
  def update_profile_picture():
      file = request.files['profile_picture']
      if file:
          picture_file = save_picture(file, folder='profile_pics', size=(150, 150))
          current_user.profile_image = picture_file
          db.session.commit()
  ```


- **File Validation**: Checking the type and size of uploaded files.
  ```python
  def allowed_file(filename, allowed_extensions=None):
      if allowed_extensions is None:
          allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
      return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
  ```


- **Secure Storage**: Generating random file names and checking paths.
  ```python
  random_hex = secrets.token_hex(8)
  _, file_ext = os.path.splitext(form_picture.filename)
  picture_filename = random_hex + file_ext
  ```


- **Image Processing**: Resizing for optimization.
  ```python
  img = Image.open(form_picture)
  img.thumbnail(size)
  img.save(picture_path)
  ```




## 2.10. Object-Oriented Programming


The project is entirely built using OOP principles:


- **Model Classes**: Structured data representation.
  ```python
  class User(db.Model, UserMixin):
      """User model for authentication and user management"""
      __tablename__ = 'users'
     
      # Class attributes and methods
     
      def set_password(self, password):
          """Set password hash from plain text password"""
          self.password_hash = generate_password_hash(password)
     
      def check_password(self, password):
          """Check if password matches the hash"""
          return check_password_hash(self.password_hash, password)
  ```


- **Encapsulation**: Hiding implementation details and providing an interface.
  ```python
  # Encapsulation of password checking logic
  def check_password(self, password):
      return check_password_hash(self.password_hash, password)
 
  # Using the method without knowing implementation details
  if user.check_password(form.password.data):
      login_user(user)
  ```


- **Inheritance**: Extending base classes to add functionality.
  ```python
  # Inheriting from db.Model and UserMixin
  class User(db.Model, UserMixin):
      # User model implementation
 
  # Inheriting from FlaskForm
  class LoginForm(FlaskForm):
      # Form field definitions
  ```


- **Polymorphism**: Using one interface for different types.
  ```python
  # Polymorphism through SQLAlchemy relationships
  # The same method works with different types of related objects
  post.author  # Accessing the post author
  comment.user  # Accessing the comment author
  ```


- **Modularity**: Dividing code into logical components.
  ```python
  # Modules for various functions
  from app.utils.file_utils import save_picture
  from app.utils.email_utils import send_reset_email
  from app.utils.ai.sentiment_analysis import analyze_sentiment
  ```


### 2.11. Refactoring to OOP


The project demonstrates full application of the OOP approach:


- **Application Factory**: Pattern for creating application instances.
  ```python
  def create_app(test_config=None):
      """Application factory function"""
      app = Flask(__name__, instance_relative_config=True)
      # Configuration and initialization
      return app
  ```


- **Blueprints**: Modular organization of routes.
  ```python
  auth_bp = Blueprint('auth', __name__)
 
  @auth_bp.route('/login', methods=['GET', 'POST'])
  def login():
      # Login logic
  ```


- **Service Classes**: Separating business logic into separate classes.
  ```python
  class SentimentAnalyzer:
      """Class for analyzing text sentiment"""
     
      @staticmethod
      def analyze(text):
          # Sentiment analysis logic
  ```


- **Utility Modules**: Organization of helper functions.
  ```python
  # file_utils.py module
  def save_picture(form_picture, folder='uploads', size=(800, 800)):
      # Image saving logic
 
  def allowed_file(filename, allowed_extensions=None):
      # File validation
  ```


### 2.12. Modern Framework Usage


The project demonstrates modern Flask framework practices:


- **Blueprints for Modularity**: Dividing the application into logical modules.
  ```python
  # Blueprint registration
  app.register_blueprint(main_bp)
  app.register_blueprint(auth_bp)
  app.register_blueprint(posts_bp)
  app.register_blueprint(errors_bp)
  ```


- **Jinja2 for Templates**: Powerful template system.
  ```html
  <!-- Template inheritance -->
  {% extends "base.html" %}
 
  <!-- Content blocks -->
  {% block content %}
      <!-- Page content -->
  {% endblock %}
 
  <!-- Conditional logic -->
  {% if current_user.is_authenticated %}
      <!-- Content for authenticated users -->
  {% else %}
      <!-- Content for guests -->
  {% endif %}
  ```


- **Bootstrap for Responsive Design**: Modern user interface.
  ```html
  <!-- Using Bootstrap components -->
  <div class="card">
      <div class="card-header">
          <h2 class="card-title">{{ post.title }}</h2>
      </div>
      <div class="card-body">
          {{ post.content }}
      </div>
  </div>
  ```


- **Context Processors**: Adding global variables to templates.
  ```python
  @app.context_processor
  def inject_now():
      return {'now': datetime.utcnow()}
  ```


- **Error Handlers**: Custom pages for HTTP errors.
  ```python
  @errors_bp.app_errorhandler(404)
  def error_404(error):
      return render_template('errors/404.html'), 404
  ```


## 3. Artificial Intelligence Integration


The project includes two key AI functions that significantly enhance the user experience:


### 3.1. Comment Sentiment Analysis


#### Technology
- **TextBlob**: A natural language processing library that uses machine learning to analyze text.


#### Implementation
- **Sentiment Analysis Module**: A specialized `sentiment_analysis.py` module was created.
  ```python
  def analyze_sentiment(text):
      """Analyze the sentiment of a text using TextBlob"""
      if not text:
          return {'polarity': 0.0, 'subjectivity': 0.0, 'sentiment': 'neutral'}
     
      # Text cleaning
      cleaned_text = clean_text(text)
     
      # Creating a TextBlob object
      blob = TextBlob(cleaned_text)
     
      # Getting sentiment
      polarity = blob.sentiment.polarity
      subjectivity = blob.sentiment.subjectivity
     
      # Determining sentiment category
      if polarity > 0.1:
          sentiment = 'positive'
      elif polarity < -0.1:
          sentiment = 'negative'
      else:
          sentiment = 'neutral'
     
      return {
          'polarity': polarity,
          'subjectivity': subjectivity,
          'sentiment': sentiment
      }
  ```


- **Integration with Comment Model**: Fields were added to store analysis results.
  ```python
  class Comment(db.Model):
      # Standard fields
     
      # Sentiment analysis fields
      sentiment = db.Column(db.String(20), default='neutral')
      sentiment_polarity = db.Column(db.Float, default=0.0)
      sentiment_subjectivity = db.Column(db.Float, default=0.0)
     
      def analyze_sentiment(self):
          """Analyze the sentiment of the comment content"""
          from app.utils.ai.sentiment_analysis import analyze_sentiment
         
          result = analyze_sentiment(self.content)
          self.sentiment = result['sentiment']
          self.sentiment_polarity = result['polarity']
          self.sentiment_subjectivity = result['subjectivity']
  ```


- **Automatic Analysis When Creating a Comment**: Integration into the comment addition process.
  ```python
  @posts_bp.route('/post/<int:post_id>/comment', methods=['POST'])
  @login_required
  def add_comment(post_id):
      # Comment creation
      comment = Comment(
          content=form.content.data,
          post_id=post.id,
          user_id=current_user.id
      )
     
      # Sentiment analysis
      comment.analyze_sentiment()
     
      db.session.add(comment)
      db.session.commit()
     
      # Different messages depending on sentiment
      sentiment_messages = {
          'positive': 'Your positive comment has been added! 😊',
          'negative': 'Your comment has been added, though it seems negative. 😞',
          'neutral': 'Your comment has been added! 😐'
      }
      flash(sentiment_messages.get(comment.sentiment, 'Your comment has been added!'), 'success')
  ```


- **Sentiment Visualization**: Displaying analysis results in the interface.
  ```html
  <div class="d-flex justify-content-end">
      <small class="text-muted">
          Sentiment: <span class="badge {% if comment.sentiment == 'positive' %}bg-success{% elif comment.sentiment == 'negative' %}bg-danger{% else %}bg-secondary{% endif %}">
              {{ comment.sentiment }} {{ comment.get_sentiment_emoji() }}
          </span>
      </small>
  </div>
  ```


#### Benefits
- **Improved Moderation**: Quick identification of potentially negative comments.
- **Sentiment Analytics**: Understanding the overall tone of discussions.
- **Enhanced User Experience**: Visual feedback about comment tone.


### 3.2. Content Recommendation System


#### Technology
- **scikit-learn**: Machine learning library for text vectorization and similarity calculation.
- **TF-IDF**: Text vectorization method that considers word frequency and importance.
- **Cosine Similarity**: Metric for determining similarity between documents.


#### Implementation
- **Recommendation Module**: A specialized `recommendation.py` module was created.
  ```python
  def build_recommendation_model(posts):
      """Build the recommendation model using TF-IDF vectorization"""
      # Extracting text and IDs
      documents = []
      post_ids = []
     
      for post in posts:
          # Combining title and content
          text = f"{post.title} {post.content}"
          documents.append(text)
          post_ids.append(post.id)
     
      # Creating and training the vectorizer
      vectorizer = TfidfVectorizer(
          max_features=5000,
          stop_words='english',
          min_df=2,
          ngram_range=(1, 2)
      )
     
      # Transforming documents into TF-IDF features
      features = vectorizer.fit_transform(documents)
     
      # Saving the model
      joblib.dump(vectorizer, get_model_path(VECTORIZER_FILE))
      joblib.dump(features, get_model_path(FEATURES_FILE))
      joblib.dump(post_ids, get_model_path(POST_IDS_FILE))
     
      return vectorizer, features, post_ids
  ```


- **Finding Similar Posts**: Function for finding content with similar content.
  ```python
  def get_similar_posts(post_id, num_recommendations=3):
      """Get similar posts based on content similarity"""
      # Loading the model
      vectorizer, features, post_ids = load_recommendation_model()
     
      # Finding the post index
      post_index = post_ids.index(post_id)
     
      # Getting the feature vector for the post
      post_vector = features[post_index:post_index+1]
     
      # Calculating similarity with all other posts
      similarities = cosine_similarity(post_vector, features).flatten()
     
      # Getting indices of similar posts
      similar_indices = similarities.argsort()[:-num_recommendations-2:-1]
     
      # Filtering out the post itself
      similar_indices = [i for i in similar_indices if i != post_index]
     
      # Getting IDs of similar posts
      similar_post_ids = [post_ids[i] for i in similar_indices]
     
      return similar_post_ids
  ```


- **Personalized Recommendations**: Recommendations based on user interaction history.
  ```python
  def get_user_recommendations(user_id, posts, num_recommendations=5):
      """Get personalized recommendations for a user"""
      # Getting posts the user has commented on
      user_commented_posts = db.session.query(Post.id).join(
          Post.comments
      ).filter_by(user_id=user_id).all()
     
      user_commented_post_ids = [p[0] for p in user_commented_posts]
     
      # Getting recommendations for each post
      recommended_post_ids = set()
      for post_id in user_commented_post_ids:
          similar_post_ids = get_similar_posts(post_id, num_recommendations=2)
          recommended_post_ids.update(similar_post_ids)
     
      # Removing posts the user has already commented on
      recommended_post_ids = recommended_post_ids - set(user_commented_post_ids)
     
      # Getting post objects
      recommended_posts = Post.query.filter(
          Post.id.in_(recommended_post_ids),
          Post.published == True
      ).order_by(Post.created_at.desc()).limit(num_recommendations).all()
     
      return recommended_posts
  ```


- **Interface Integration**: Displaying recommendations in the user interface.
  ```html
  <!-- Similar posts section -->
  <div class="card mb-4">
      <div class="card-header bg-primary text-white">
          <h2 class="h5 mb-0"><i class="fas fa-robot me-2"></i>AI-Recommended Similar Posts</h2>
      </div>
      <div class="card-body">
          <div class="row">
              {% for similar_post in similar_posts %}
                  <!-- Similar post display -->
              {% endfor %}
          </div>
      </div>
  </div>
  ```


- **Personal Recommendations Page**: Special page with recommendations.
  ```python
  @posts_bp.route('/recommendations')
  @login_required
  def recommendations():
      """Show personalized post recommendations for the current user"""
      # Getting recommendations for the current user
      recommended_posts = Post.get_recommendations_for_user(current_user.id, limit=5)
     
      return render_template('posts/recommendations.html',
                            title='Recommended Posts',
                            posts=recommended_posts)
  ```


#### Benefits
- **Improved Content Discovery**: Users can find relevant content.
- **Personalization**: Recommendations based on user interests.
- **Increased Engagement**: Users spend more time on the platform.


## 4. Technical Requirements


The project fully meets all technical requirements:


- **Python 3.x**: Using a modern Python version.
- **Flask Framework**: The foundation of the web application.
- **HTML5, CSS3 with Bootstrap**: Modern, responsive user interface.
- **SQLAlchemy ORM**: Object-relational mapping for database work.
- **Jinja2 Templates**: Powerful template system for HTML generation.
- **WTForms**: Library for creating and validating forms.
- **Git Repository**: Version control system for code management.
- **AI/ML Libraries**: TextBlob, scikit-learn for AI integration.


## 5. Results


The project is a full-featured blog platform with artificial intelligence integration:


- **Blog Functionality**: Creating, editing, deleting posts and comments.
- **User System**: Registration, login, profile management.
- **AI Integration**: Sentiment analysis and content recommendations.
- **Modern Interface**: Responsive design using Bootstrap.
- **Security**: Password hashing, CSRF protection, input validation.
- **Modular Architecture**: Using Blueprints and OOP.


### Screenshots of Key Pages


[Screenshots of the main application pages should be placed here]


### Conclusion


The project demonstrates the comprehensive application of modern web technologies and artificial intelligence to create a full-featured web application. AI integration significantly enhances the user experience, providing additional features for sentiment analysis and personalized recommendations.


The project fully meets all requirements of the final assignment, demonstrating both technical web development skills and understanding of applying artificial intelligence technologies in real applications.




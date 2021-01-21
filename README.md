# Fundoo Notes

### This project contains two app:
### 1. Login-Registration: contains Login, Logout ,Email verification, Forgotpassword, Resetpassword. Used jwt for token creation.                                       
### 2. Note: User can create notes, label.


 ### Description :
- **Login-Registration** provides APIs for following features:
    * Registration using email verification.
    * Login and logout
    * Reset password
- For authentication JWT token is used. 
- For user profile creation signal is used.

* **Note** app provides API's for following features :
    * List notes
    * Create and list Notes
    * Update, delete Notes
    * Create and list labels
    * Update, delete label
    * Archive Note
    * UnArchive Note
    * Trash Note
    * UnTrash Note
    * Search 
    * collaborator
    * Reminder
    
* **JWT Token :** JWT is an encoded JSON string that is passed in headers to authenticate requests. It is usually obtained by hashing JSON data with a secret key. This means that the server doesn't need to query the database every time to retrieve the user associated with a given token.

* **The Concept of Authentication and Authorization :**Authentication is the process of identifying a logged-in user, while authorization is the process of identifying if a certain user has the right to access a web resource.

* **Signals :**  Django includes a “signal dispatcher” which helps allow decoupled applications get notified when actions occur elsewhere in the framework. In a nutshell, signals allow certain senders to notify a set of receivers that some action has taken place. They’re especially useful when many pieces of code may be interested in the same events.

* **Celery :** We can call a celery task by two ways:
    * Synchronous : The method is exceuted in same thread.
    * Asynchronous : The message is sent to celery worker by using rabbitMQ server. Ex : method_name.delay() : It create json message and paass it to celery worker.
    * Celery uses rabbitMQ serve as message broker that passes the message from django to celery worker.
    * By using status property we can check status of asychronous tasks.
    
## Prerequirement
  * Python 3
## Install packages using:
* pip install -r requirements.txt

# Database connection with project
- In settings.py file :
  
1. For  mongodb :
   
        DATABASES = {
      
          'default': {
   
            'ENGINE': 'djongo',
               'NAME': 'database_name',
           }
   
        }

2. For Postgres :

        DATABASES = {
          'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'database name',
            'USER': 'postgres',
            'PASSWORD': 'password',
            'PORT': '5432',
          }
        }

## SonarQube Analysis:
 ### Install sonarQube from zipfile:

* Download sonarQube community version from this link : https://www.sonarqube.org/downloads/
* Unzip it and configure properties and config files inside conf folder:
  * sonar.properties file :
    
    a. Setting the Access to the Database:Uncomment these lines and set variables Example for PostgreSQL
    
      * sonar.jdbc.username=sonarqube
      * sonar.jdbc.password=
      * sonar.embeddedDatabase.port=9092
      * sonar.jdbc.url=jdbc:postgresql://localhost/sonarqube?currentSchema=my_schema
    
    b.  Starting the Web Server
      * sonar.web.host=127.0.0.1
      * sonar.web.context=
      * sonar.web.port=9000
  
* Execute the following script to start the server:
  * On Linux: bin/linux-x86-64/sonar.sh start
  * On macOS: bin/macosx-universal-64/sonar.sh start
  * On Windows: bin/windows-x86-64/StartSonar.bat
	We can now brot System administrator credentials are admin/admin).wse SonarQube at http://localhost:9000 (the default System administrator credentials are admin/admin).
*   After the installation:
    * After server is up and running, we'll need to install one or more SonarScanners on the machine where analysis will be performed.
    * Use this link to download: https://docs.sonarqube.org/latest/analysis/scan/sonarscanner/
  
### Running SonarScanner from the zip file

To run SonarScanner from the zip file, follow these steps:

  * Expand the downloaded file into the directory of your choice. We'll refer to it as $install_directory in the next steps.
  * Update the global settings to point to your SonarQube server by editing $install_directory/conf/sonar-scanner.properties:
      * sonar.host.url=http://localhost:9000
  * Add the $install_directory/bin directory to your path.
  * Verify installation by opening a new shell and executing the command sonar-scanner -h (sonar-scanner.bat -h on Windows). Output soulbe be like this:

        usage: sonar-scanner [options]
        Options:
        -D,--define <arg>     Define property
        -h,--help             Display help information
        -v,--version          Display version information
        -X,--debug            Produce execution debug output
### Configuring your project:
  * Create a configuration file in your project's root directory called sonar-project.properties:

        - sonar.projectKey=my:project
        - #sonar.projectName=My project
        - #sonar.projectVersion=1.0
        - #sonar.sources=.
        - #sonar.sourceEncoding=UTF-8
### Launching the project:
  * Give a project on the server
  * Generate a token
  * Run the following command from the project base directory to launch analysis and pass your authentication token:

        sonar-scanner -Dsonar.login=myAuthenticationToken
### Now browse SonarQube at http://localhost:9000 : 

## Redis Installation :
* **About redis :** Redis is an in-memory data structure store that can be used as a caching engine. Since it keeps data in RAM, Redis can deliver it very quickly. Redis is not the only product that we can use for caching.
* Use this link to download redis for Linux: https://redis.io/download
* For more documentation refer this link: https://redis.io/documentation

* Open command prompt and give following command to start redis server:
    * redis-cli
    * Type ping to check if server is started or not. it should return pong as response.
  
### Redis cache implementation :
  * Set custom cache backend in settings :

        CACHES = {
          "default": {
            "BACKEND": "django_redis.cache.RedisCache", 
            "LOCATION": "redis://127.0.0.1:6379/1",
            "OPTIONS": {
              "CLIENT_CLASS": "django_redis.client.DefaultClient",
              "TIMEOUT": 3600
            },
            "KEY_PREFIX": "keep"
          }
        }
* Accessing the cache:
    * import : from django.core.cache import cache
    * cache.set(key, value, timeout=DEFAULT_TIMEOUT, version=None)
    * cache.get(key, default=None, version=None)
* For each API call check if data is present in cache or not by using cache.get(key).

* If it is there then retrieve data from to cache only otherwise perform query on database and set that data to cache by using cache.set(key, data). So that next time that data can be retrieved from cache.

### RabbitMQ  Installation:

* First we need to download and install erlang by giving following command:
                              
      - sudo apt-get install erlang
* Then start the server by using following commands:

      - sudo systemctl enable rabbitmq-server
      - sudo systemctl start rabbitmq-server 
      - sudo systemctl status rabbitmq-server
* Then enable management service and then add user and password or by default username and password is both "guest".

      - sudo rabbitmqctl-plugins enable rabbitmq_management
      - sudo rabbitmqctl add_user "name" "password".
      - sudo rabbitmqctl add_user_tags "name" administrator
      - sudo rabbitmqctl set_permissions -p / name "." "." "."

### Celery Basic Setup:
* Install celery using following commands:
  
      - pip install celery 
      * To start celery worker use:
        - celery -A "Project_name" worker
        - celery -A "Project_name" worker -l info
  
* Add the CELERY_BROKER_URL configuration to the settings.py file :

      CELERY_BROKER_URL = 'amqp://localhost'
* In project root folder create a new file named celery.py and add the following code in that :

      import os
      from celery import Celery

      os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_name.settings')

      app = Celery('project_name')
      app.config_from_object('django.conf:settings', namespace='CELERY')
      app.autodiscover_tasks()
* Now edit the init.py file in the project root:

      from .celery import app as celery_app
      __all__ = ['celery_app']
* Create a file named tasks.py inside a Django app and put all our Celery tasks into this file. Basic structure is here :

      from celery import shared_task

      @shared_task
      def name_of_your_function(optional_param):
          pass  # do something heavy
* Starting The Worker Process : Open a new terminal tab, and run the following command:

      celery -A mysite worker -l info

### Asychronous tasks in celery:
* To check the task status install django_celery_results package. It store the status of tasks in databse table.

* We have to add this in installed apps settings and then migrate.

* Add Celery backend as django database in settings :

      CELERY_RESULT_BACKEND = 'django-db'
* Add celery cache as django cache also in settings:

      CELERY_CACHE_BACKEND = 'django-cache'

### Setting periodic tasks in celery:

* Install celery_beat extension for this and add it to installed apps in settings.

* After this migrate all migrations.

* Then celery.py file add the configuration for schedule beat like tasks name, scheduling time, and arguments for the method:

      app.conf.beat_schedule = {
          'triggering' : {
              'task': 'Notes.tasks.send_email',
              'schedule': 15,
              'args': ('malibharti5@gmail.com',)
          }
      }
* To set schedule time we can use contrab and sonar schedulers also like this:

      contrab(minutes='*/15')

### Executing celery task:
* Run command :
      
      celery -A KeepNotes beat -l info
### Monitoring Celery tasks:

* **celery -A KeepNotes status** : To check the status of every runnning worker.
* **celery -A KeepNotes inspect** : It take an agrguments like the following -
    1. active : Shows all running tasks in worker.
    2. reserved : Displays reserved tasks means those tasks that are not started and scheduled over max limit of worker. So these tasks will be executed whenever the worker will be free.
    3. schedule : Shows the periodic tasks.To set periodic tasks we have to set ETA or countdown parameters whilw calling asynchronous tasks.
  
### References :
* For redis cache implementation : https://docs.djangoproject.com/en/3.1/topics/cache/
* For rabbitMQ installation :
  * ubuntu : https://simpleisbetterthancomplex.com/tutorial/2017/08/20/how-to-use-celery-with-django.html
  * windows : https://www.youtube.com/watch?v=V9DWKbalbWQ
* For celery :
  1. https://simpleisbetterthancomplex.com/tutorial/2017/08/20/how-to-use-celery-with-django.html
  2. https://www.youtube.com/watch?v=A89mCa1ytow

### Author:
Ranjith.P
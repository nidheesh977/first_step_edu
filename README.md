## Deploying notes.
* create "profilePictures" folder under media and add user.png
* deploying server must have python 3.10 or above version 



# Project Details
* application(application name) is an frontend integrated application
* admin_dashboard application is for client admin
#### Project application
* for marquee text in home page just refer the first_edu/context_processors.py
* root folder is first_edu
* application/templates/application_base.html ->  this page contains header, footer, navbar,Ask us here(container)
* application/templates/index.html -> only home page contents
* for blog prefix url i'm using the .env file. this blog prefix only will call globally in all of the blog listing and detail 
    pages(both appication views and html).

### Admin Dashboard
* in admin dashboard image size(hxw) restrictions are there while uploading images. size configurations are in the utils/constants.py
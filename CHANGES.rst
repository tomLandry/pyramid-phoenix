Changes
*******

0.5.0 (2016-07-11)
==================

* using zc.recipe.deployment.
* using new buildout recipes.
* using conda environment.yml
* possible to edit job caption in monitor view.
* monitor view allows tagging of jobs and filter with tags.
* using special tag "public" to set job as public accessable.
* monitor: only show progress for running jobs.

0.4.8 (2016-07-11)
==================

* Update user_guide.rst
* fixed catalog search filter (#91)
* fixed keywords display of thredds servcices (#91)
* pinned mongodb=2 ... update pywps=3.2.6
* added default password
* pinned netcdf4=1.2.2 and added ioos channel to conda part
* update twitcher 0.1.7

0.4.7 (2016-06-06)
==================

* display process metadata in processes view.
* ncwms, solr and pycsw are now optional build parts and moved to advanced.cfg.
* by default using the catalog based on MongoDB ... optionally one can use pycsw.
* update to pyramid 1.7
* using service_name for wps from twitcher registry.
* restart job from monitor view (using linage info).
* using lineage info from wps protocol for input parameters.


0.4.6 (2016-05-10)
==================

* added public access for jobs.
* enabled guest account.
* added filter and pagination in monitor view.
* using twitcher security proxy.

0.4.5 (2016-04-22)
==================

* updated mongodb: using non default port.
* added solr search in wizard.
* index thredds services to solr in settings.

0.4.4 (2015-06-30)
==================

* auth settings page added.
* fixed swiftlogin.
* allow edit of user emails.
* fixed wizard favorites loading.
* fixed account validation form.
* show username in navigation bar.

0.4.3 (2015-06-25)
==================

* cleaned up nginx template.
* added user option for supervisor, nginx.

0.4.2 (2015-06-24)
==================

* cleaned up default layout.
* enabled https.

0.4.1 (2015-06-22)
==================

* added Phoenix login
* added GitHub login
* added LDAP login
* refactored

0.4.0 (2015-06-14)
==================

* register thredds catalogs.
* bugfixes.
* added thredds as source in wizard.
* added supervisor view.
* refactored.
* Added help button pointing to phoenix documentation on readthedocs.

0.3.0 (2015-02-24)
==================

* Now possible to use shared anaconda installation.

0.2.3 (2015-02-23)
==================

* sets x509 proxy certificate in processes.
* using TimedRotatingFileHandler for logging.
* esgf search is by default not distributed.
* default log-level set to info.
* map disabled (needs refactoring)
* calling dispel workflow on malleefowl
* skipped esgf file selection ... file search is done in dispel workflow  

0.2.2 (2014-11-24)
==================

Utrecht Release

* sends email to admin users on user login failure.
* uses user name from openid parameters.
* added provider for each contry to esgf login page.
* shows last login in users settings.
* shows unregistered users in dashboard.
* using buildout 2.x.

Bugs:

* Fixed start problems with supervisor: 
csw, wps and mongodb are now initialized on first request (not on start time)

0.2.1 (2014-11-11)
==================

* Using Makefile from birdhousebuilder.bootstrap to install and start application.
* Fixed signin urls on register page.


0.2.0 (2014-09-04)
==================

Paris Release


* moved code to github
* choose licence: apache license version 2.0
  http://www.apache.org/licenses/
* setup proxy for openlayers and js to access thredds, esgf-search ...
  https://github.com/gwaldron/godzi-webgl/blob/master/tests/proxy.php
  http://trac.osgeo.org/openlayers/wiki/FrequentlyAskedQuestions#ProxyHost
  http://wiki.nginx.org/HttpFastcgiModule
* configure base malleefowl wps + additional wps from catalog service
* use simple wps calls in wizard for listings etc ...
* use wps chain for restflow process
* reduce number of wps initialisations in wizard
* uses datetime json renderer:
http://docs.pylonsproject.org/projects/pyramid/en/1.5-branch/narr/renderers.html#json-renderer
* dashboard added
* refactored wizard

Bugs

* time selection does not filter mon cordex files in esg file search
* init of wps fails (e.a when wps is registered but not avail)
* fix port 80 config (browserid ...)
* notes and tags missing in job list

0.1.1 (2014-05-20)
==================

Helsinki Release

* added ipython notebook tutorials

0.1.0 (2013-12-10)
==================

Hamburg Release


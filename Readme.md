# Bauble.web

This is web based version of Bauble.  It is in development and isn't currently
in a usable state.

### Setup local environment

```sh
cd bauble.web
pyenv virtualenv bauble
pyenv activate bauble
pip install -r requirements-dev.txt
npm install -g browserify babel ng-annotate
npm install -d
```

### Run tests

`./manage.py test`

or

`py.test`

### Start dev server

`./manage.py livereload`

from app.application import make_application

(app, router, webserver) = make_application()

router.get('/', 'HomeController@index')
router.get('/settings', 'SettingsController@get')
router.post('/response', 'ResponseController@store')
router.get('/static/{filename}', 'StaticFilesController@show')

for method in webserver.respond_to_http_verbs:
    router.register_route(
        method, '/response/{uuid}', 'ResponseController@show')


app.start()

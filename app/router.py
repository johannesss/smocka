import inspect
import os
import pkgutil
import re
from importlib import import_module
from os.path import dirname


class MethodNotAllowedException(Exception):
    pass


class PathNotFoundException(Exception):
    pass


class ControllerNotFound(Exception):
    pass


class ControllerMethodNotCallable(Exception):
    pass


class ControllerMethodNotFound(Exception):
    pass


class NoResponseReturnedFromControllerMethod(Exception):
    pass


class Router:
    def __init__(self):
        self._routes = {}
        self._controllers = {}

    def get(self, path, identifier):
        self.register_route('GET', path, identifier)

    def post(self, path, identifier):
        self.register_route('POST', path, identifier)

    def put(self, path, identifier):
        self.register_route('PUT', path, identifier)

    def delete(self, path, identifier):
        self.register_route('DELETE', path, identifier)

    def patch(self, path, identifier):
        self.register_route('PATCH', path, identifier)

    def register_route(self, http_method, path, identifier):
        (controller_name, controller_method) = identifier.split('@')

        self._register_controller(
            controller_name, controller_method)

        params = self._extract_params_from_route_path(path)

        route = {
            'controller': controller_name,
            'method': controller_method,
            'params': params,
            'pattern': self._compile_route_pattern(path, params)
        }

        if path not in self._routes:
            self._routes[path] = {}
            self._routes[path][http_method] = route
        else:
            self._routes[path][http_method] = route

        print("""
==============================

Registering {} for path '{}'

Pattern: {}

Params: {}

==============================
""".format(
            http_method, path, route['pattern'], params
        ))

    def _compile_route_pattern(self, path, params):
        if params is not None:
            for match in params:
                if match == params[-1]:
                    path = path.replace(match, r'([^/]+)')
                else:
                    path = path.replace(match, r'(.+?)')

            return "^{}".format(path)

    def _extract_params_from_route_path(self, path):
        regex = r"{.+?}"

        pattern_contains_params = re.search(regex, path)

        if pattern_contains_params is None:
            return None

        return re.findall(regex, path, re.DOTALL)

    def _get_controller_method(self, request_method, path_methods):
        route = path_methods.get(request_method)

        controller_name = route.get('controller')
        controller = self._controllers.get(controller_name)

        controller_method = route.get('method')

        return getattr(controller, controller_method)

    def _match(self, request):
        req_path = request.path().split('?')[0]  # remove query string
        req_meth = request.method()

        match = None

        for path, methods in self._routes.items():
            has_params = "{" in path
            if not has_params:
                if path == req_path:
                    if req_meth in methods:
                        controller_method = self._get_controller_method(
                            req_meth, methods)

                        match = {
                            'controller_method': controller_method,
                            'params': None
                        }

            else:
                # parameters in path, match using regex
                if req_meth in methods:
                    pattern = methods[req_meth]['pattern']
                    if re.match(pattern, req_path) is not None:
                        params = re.findall(pattern, req_path)

                        controller_method = self._get_controller_method(
                            req_meth, methods)

                        if type(params[0]) is tuple:
                            match = {
                                'controller_method': controller_method,
                                'params': params[0]
                            }
                        else:
                            match = {
                                'controller_method': controller_method,
                                'params': params
                            }

        if match is not None:
            if match['params']:
                response = match['controller_method'](
                    request, *match['params'])
            else:
                response = match['controller_method'](request)

            if response is None:
                raise NoResponseReturnedFromControllerMethod

            return response

        raise PathNotFoundException(
            "Path '{}' was not found.".format(req_path))

    def _validate_controller_method(self, instance, method):
        method_exists = hasattr(instance, method)
        controller_name = instance.__class__.__name__

        if not method_exists:
            raise ControllerMethodNotFound(
                "Method '{}' does not exist in controller '{}'.".format(
                    method, controller_name
                ))

        is_callable = callable(getattr(instance, method))

        if not is_callable:
            raise ControllerMethodNotCallable(
                "Attribute '{}' in controller '{}' not callable.".format(
                    method, controller_name
                )
            )

    def _resolve_cached_controller_instance(self, controller_name):
        if controller_name in self._controllers:
            instance = self._controllers.get(controller_name)

            print("Retrieving controller instance for '{}' from cache."
                  .format(controller_name))

            return instance

    def _find_and_return_controller_instance(self, controller_name):
        root_dir = dirname(os.path.dirname(os.path.abspath(__file__)))
        controller_path = root_dir + '/app/controllers'

        for (_, name, _) in pkgutil.iter_modules([controller_path]):
            imported_module = import_module(
                '.' + name, package='app.controllers')

            for i in dir(imported_module):
                attribute = getattr(imported_module, i)

                is_match = inspect.isclass(
                    attribute) and attribute.__name__ == controller_name

                if not is_match:
                    continue

                instance = attribute()

                return instance

        raise ControllerNotFound(
            "Controller '{}' was not found.".format(controller_name))

    def _register_controller(self, controller_name, controller_method):
        instance = self._resolve_cached_controller_instance(
            controller_name)

        if not instance:
            instance = self._find_and_return_controller_instance(
                controller_name)

            self._controllers[controller_name] = instance

            print("Registered controller '{}'.".format(controller_name))

        self._validate_controller_method(instance, controller_method)

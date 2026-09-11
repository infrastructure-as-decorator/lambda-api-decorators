def GET(path):
    def decorator(fun):
        def wrapper(*args,  **kwargs):
            result = fun(*args, **kwargs)
            return result
        return wrapper
    return decorator

def PUT(path):
    def decorator(fun):
        def wrapper(*args,  **kwargs):
            result = fun(*args, **kwargs)
            return result
        return wrapper
    return decorator

def POST(path):
    def decorator(fun):
        def wrapper(*args,  **kwargs):
            result = fun(*args, **kwargs)
            return result
        return wrapper
    return decorator

def DELETE(path):
    def decorator(fun):
        def wrapper(*args,  **kwargs):
            result = fun(*args, **kwargs)
            return result
        return wrapper
    return decorator

def ANY(path):
    def decorator(fun):
        def wrapper(*args,  **kwargs):
            result = fun(*args, **kwargs)
            return result
        return wrapper
    return decorator

def memory_size(arg):
    def decorator(fun):
        def wrapper(*args,  **kwargs):
            result = fun(*args, **kwargs)
            return result
        return wrapper
    return decorator

def timeout(arg):
    def decorator(fun):
        def wrapper(*args,  **kwargs):
            result = fun(*args, **kwargs)
            return result
        return wrapper
    return decorator

def environment(*eargs,  **kwargs):
    def decorator(fun):
        def wrapper(*args,  **kwargs):
            result = fun(*args, **kwargs)
            return result
        return wrapper
    return decorator

def layer(*largs,  **kwargs):
    def decorator(fun):
        def wrapper(*args,  **kwargs):
            result = fun(*args, **kwargs)
            return result
        return wrapper
    return decorator

def runtime(arg):
    def decorator(fun):
        def wrapper(*args,  **kwargs):
            result = fun(*args, **kwargs)
            return result
        return wrapper
    return decorator

def security_group(*sgargs):
    def decorator(fun):
        def wrapper(*wargs,  **kwargs):
            result = fun(*wargs, **kwargs)
            return result
        return wrapper
    return decorator

def vpc(arg):
    def decorator(fun):
        def wrapper(*args,  **kwargs):
            result = fun(*args, **kwargs)
            return result
        return wrapper
    return decorator

def role(arg):
    def decorator(fun):
        def wrapper(*args,  **kwargs):
            result = fun(*args, **kwargs)
            return result
        return wrapper
    return decorator

def description(arg):
    def decorator(fun):
        def wrapper(*args,  **kwargs):
            result = fun(*args, **kwargs)
            return result
        return wrapper
    return decorator

def name(arg):
    def decorator(fun):
        def wrapper(*args,  **kwargs):
            result = fun(*args, **kwargs)
            return result
        return wrapper
    return decorator

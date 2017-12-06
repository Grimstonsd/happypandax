query_string = require("query-string")
moment = require("moment")
isEqual = require('lodash/isEqual')

syntax_highlight = __pragma__('js', '{}',
                              """
    function syntax_highlight(json) {
        json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
        return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
            var cls = 'json-number';
            if (/^"/.test(match)) {
                if (/:$/.test(match)) {
                    cls = 'json-key';
                } else {
                    cls = 'json-string';
                }
            } else if (/true|false/.test(match)) {
                cls = 'json-boolean';
            } else if (/null/.test(match)) {
                cls = 'json-null';
            }
            return '<span class="' + cls + '">' + match + '</span>';
        });
    }""")

poll_func = __pragma__('js', '{}',
                       """
    function poll_func(fn, timeout, interval) {
    var startTime = (new Date()).getTime();
    interval = interval || 1000;
    var canPoll = true;

    (function p() {
        canPoll = ((new Date).getTime() - startTime ) <= timeout;
        if (!fn() && canPoll)  { // ensures the function exucutes
            setTimeout(p, interval);
        }
    })();
    }""")

poll_func_stagger = __pragma__('js', '{}',
                               """
    function poll_func(fn, timeout, interval) {
    var startTime = (new Date()).getTime();
    interval = interval || 1000;
    var canPoll = true;

    (function p() {
        canPoll = ((new Date).getTime() - startTime ) <= timeout;
        interval = fn()
        if (interval && canPoll)  { // ensures the function exucutes
            setTimeout(p, interval);
        }
    })();
    }""")

storage_available = __pragma__('js', '{}',
                               """
function storageAvailable(type) {
    try {
        var storage = window[type],
            x = '__storage_test__';
        storage.setItem(x, x);
        storage.removeItem(x);
        return true;
    }
    catch(e) {
        return e instanceof DOMException && (
            // everything except Firefox
            e.code === 22 ||
            // Firefox
            e.code === 1014 ||
            // test name field too, because code might not be present
            // everything except Firefox
            e.name === 'QuotaExceededError' ||
            // Firefox
            e.name === 'NS_ERROR_DOM_QUOTA_REACHED') &&
            // acknowledge QuotaExceededError only if there's something already stored
            storage.length !== 0;
    }
}
                               """)


defined = __pragma__('js', '{}',
                     """
    function defined(v) {
        return !(v === undefined);
    }""")


def get_locale():
    return window.navigator.userLanguage or window.navigator.language


def query_to_string(obj):
    return query_string.stringify(obj)

__pragma__("kwargs")


def query_to_obj(query=None, location_obj=None):
    if not query:
        l = location_obj or location
        query = l.search
    return query_string.parse(query)
__pragma__("nokwargs")

__pragma__("kwargs")
__pragma__("iconv")


def get_query(key, default=None, query=None, location_obj=None):
    q = {}
    q.update(query_to_obj(query, location_obj=location_obj))
    if key in q:
        return q[key]
    return default
__pragma__("noiconv")
__pragma__("nokwargs")

__pragma__("kwargs")
__pragma__("tconv")


def go_to(history_obj, url="", query={}, state=None, push=True, keep_query=True, location_obj=None):
    if not url:
        l = location_obj or location
        url = l.pathname
    q = {}
    if keep_query:
        q.update(query_to_obj())
    q.update(query)

    if q:
        url += "?" + query_to_string(q, location_obj=location_obj)
    if push:
        history_obj.push(url, state)
    else:
        history_obj.js_replace(url, state)
__pragma__("notconv")
__pragma__("nokwargs")

__pragma__("kwargs")
__pragma__("tconv")


def build_url(url="", query={}, keep_query=True, location_obj=None):
    if not url:
        l = location_obj or location
        url = l.pathname
    q = {}
    if keep_query:
        q.update(query_to_obj())
    q.update(query)

    if q:
        url += "?" + query_to_string(q, location_obj=location_obj)
    return url
__pragma__("notconv")
__pragma__("nokwargs")


def scroll_to_element(el):
    if el:
        el.scrollIntoView({'behavior': 'smooth'})


def is_same_machine():
    return document.getElementById('root').dataset.machine == "True"

def get_version():
    return document.getElementById('root').dataset.version

moment.locale(get_locale())

class Storage:

    def __init__(self):
        self.dummy = {}
        self.enabled = storage_available("localStorage")
        self.lstorage = localStorage

    __pragma__("kwargs")
    def get(self, key, default=None, local=False):
        if self.enabled and not local:
            r = self.lstorage.getItem(key)
            if r is None and default is not None:
                r = default
            elif r:
                r = JSON.parse(r) # can't handle empty strings
        else:
            r = self.dummy.get(key, default)
        return r

    def set(self, key, value, local=False):
        if self.enabled and not local:
            if value == None: # convert undefined to null
                value = None
            self.lstorage.setItem(key, JSON.stringify(value))
        else:
            self.dummy[key] = value

    def clear(self, local=False):
        if self.enabled and not local:
            self.lstorage.js_clear()
        else:
            self.dummy.clear()

    def remove(self, key, local=False):
        if self.enabled and not local:
            self.lstorage.removeItem(key)
        else:
            self.dummy.pop(key, True)
    __pragma__("nokwargs")

storage = Storage()

__pragma__("kwargs")
def either(a, b=None):
    if a is None:
        return b
    return a
__pragma__("nokwargs")

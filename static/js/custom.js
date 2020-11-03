function ajax(o) {
    var u = o.u || location.protocol + '//' + location.hostname + location.pathname,
        m = o.m || 'post',
        d = o.d || '', //form id
        a = o.a || ''; //add value=>{name:value}
    return new Promise(function(resolve, reject) {
        var fd = new FormData();
        if (d) {
            fd = new FormData(d);
        }
        if (a) {
            for (var key in a) {
                fd.append(key, a[key]);
            }
        }

        // console.log(typeof(a))
        var json = JSON.stringify(a);
        var xhr = new XMLHttpRequest();
        xhr.open(m, u, true);
        xhr.onload = function() {
            resolve(JSON.parse(xhr.responseText))
        };
        xhr.onerror = function() {
            reject(JSON.parse(xhr.statusText))
        };
        xhr.send(json);
    });
};
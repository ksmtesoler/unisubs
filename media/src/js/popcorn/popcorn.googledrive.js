(function(Popcorn, document) {
    // We can't really control the google drive player, so just create a dummy
    // element that shows the embedder in an iframe, but doesn't support
    // anything else (seeking, querying, events, etc)
    Popcorn.GoogleDriveVideoElement = function(id) {
        var self = new Popcorn._MediaElementProto(),
            parent = typeof id === "string" ? Popcorn.dom.find( id ) : id,
            elem = document.createElement('iframe');
            impl = {
                src: null
            };

        self._eventNamespace = Popcorn.guid( "HTMLGoogleDriveVideoElement::" );
        self.parentNode = parent;

        function changeSrc(src) {
            elem.setAttribute('width', '640');
            elem.setAttribute('height', '480');
            elem.setAttribute('src', src);
            parent.appendChild(elem);
            impl.src = src;
        }

        Object.defineProperties( self, {
            src: {
                get: function() {
                    return impl.src;
                },
                set: function( aSrc ) {
                    if(aSrc && aSrc !== impl.src) {
                        changeSrc(aSrc);
                    }
                }
            }
        });
        return self;
    }

    Popcorn.googledrive = function(id, urls, options) {
        var media = new Popcorn.GoogleDriveVideoElement(id);
        var pop = Popcorn(media, options);
        media.src = urls[0];
        return pop;
    }
})(Popcorn, document);

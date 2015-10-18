
//
// An InstrumentedArray inherits from a native Javasript Array but
// tracks adds and removes to the array when using push() and remove()
//
function InstrumentedArray(){
    "use strict";

    if ( !(this instanceof InstrumentedArray) ) {
        return new InstrumentedArray(arguments);
    }

    var args = Array.prototype.slice.call(arguments);

    // if the first argument is an array then add all the elements to this
    if(args.length > 0 && args[0] instanceof Array) {
        Array.call(this);
        for(var i=0; i<args[0].length; i++) {
            Array.prototype.push.call(this, args[0][i]);
        }
    } else {
        Array.apply(this, args);
    }

    this.added = [];
    this.removed = [];
}

InstrumentedArray.prototype = [];  //new Array();
//InstrumentedArray.prototype = new Array();


InstrumentedArray.prototype.remove = function(object) {
    "use strict";

    var index = this.indexOf(object);
    if(index === -1) {
        throw new Error("could not find object in array");
    }

    this.splice(index, 1);

    index = this.added.indexOf(object);
    if(index !== -1) {
        this.added.splice(index, 1);
    } else {
        this.removed.push(object);
    }
};


InstrumentedArray.prototype.push = function(object) {
    "use strict";

    this.added.push(object);
    Array.prototype.push.call(this, object);
};


// var a = new InstrumentedArray(["x", "y", "z"]);
// console.log('a: ', a);
// console.log('a[0]: ', a[0]);

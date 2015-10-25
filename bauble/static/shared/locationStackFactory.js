export default function locationStackFactory ($location) {
    var storageKey = 'locationStack';

    function getStack() {
        var value = sessionStorage.getItem(storageKey);
        return value === null ? [] : JSON.parse(value);
    }

    function saveStack(stack) {
        sessionStorage.setItem(storageKey, JSON.stringify(stack));
    }

    function LocationStack() {

    }

    LocationStack.prototype.push = function(location, transition) {
        var stack = getStack();
        var index = stack.push(location instanceof String ? location : $location.url());
        saveStack(stack);
        return index;
    };

    LocationStack.prototype.pop = function(transition) {
        transition = angular.isDefined(transition) ? transition : true;
        var stack = getStack();
        var location = stack.pop();
        saveStack(stack);
        if(!transition) {
            // don't change the location
            return;
        }

        return $location.url(angular.isDefined(location) ? location : '/');
    };

    return new LocationStack();
}

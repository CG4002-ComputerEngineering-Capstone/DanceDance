function Queue () { 
  var collection = [];
  this.print = function() {
      console.log(collection);
  };
  this.enqueue = function(element) {
    collection.push(element);
    /*
    if (collection.length > 80) {
        return collection.shift();
    }
    */
  };
  this.dequeue = function() {
      return collection.shift(); 
  };
  this.front = function() {
      return collection[0];
  };
  this.size = function() {
      return collection.length; 
  };
  this.isEmpty = function() {
      return (collection.length === 0); 
  };
}

export default Queue;
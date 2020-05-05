// Based on the vanila RSA
// implement a RSA model to infer the intention of co-player
// giving me a hint about a single card

// print function 'condProb2Table' for conditional probability tables
///fold:
var condProb2Table = function(condProbFct, row_names, col_names, precision){
  var matrix = map(function(row) {
    map(function(col) {
      _.round(Math.exp(condProbFct(row).score(col)),precision)}, 
        col_names)}, 
                   row_names)
  var max_length_col = _.max(map(function(c) {c.length}, col_names))
  var max_length_row = _.max(map(function(r) {r.length}, row_names))
  var header = _.repeat(" ", max_length_row + 2)+ col_names.join("  ") + "\n"
  var row = mapIndexed(function(i,r) { _.padEnd(r, max_length_row, " ") + "  " + 
                       mapIndexed(function(j,c) {
                          _.padEnd(matrix[i][j], c.length+2," ")}, 
                                  col_names).join("") + "\n" }, 
                           row_names).join("")
  return header + row
}
///



///// game dynamics /////

// TODO: keep track of top cards, interact with Eger
var board = {blue: 1,
             green: 2,
             yellow: 1,
             white: 0,
             red: 3}
//////////////////////



///// literal listener /////

// set of states (here intention for a card)
// we represent objects as JavaScript objects to demarcate them from utterances
// internally we treat objects as strings nonetheless
var objects = [
  {string: "play"},
  {string: "keep"},
  {string: "discard"}
  ]

// prior over world states
var objectPrior = function() {
  var obj = categorical({
    vs: objects,
    ps: [3, 2, 1.5]  // arbitrary priors for intentions
  })
  return obj.string 
}

// set of possible utterances
var utterances = ["blue", "green", "yellow", "white", "red",
                 "1", "2", "3", "4", "5"]


// literal listener, p(s|u)
var literalListener = function(utterance){
  // TODO: use utterance to update knowledge structure in Eger
  Infer({model: function(){
    var obj = objectPrior(); // sample intentions according to the prior
    if (obj == "play") {
      //if (playable() {factor(1)} // TODO: interaction with Eger algorithm
      if (utterance == '1') {factor(1)}
    else {factor(0.1)}
  } 
    else  {factor(0.5)} // just arbitrary examples for now
    return obj
  }})
}
//////////////////////////////////////////////////



///// pragmatic speaker /////

// set speaker optimality
// TODO: adjust alpha value depending on whether the co-player
// played accordingly to my intention
var alpha = 1

// utterance cost function
var cost = function(utterance) {
  return 0;  // TODO: Does this makes sense?
};

// pragmatic speaker, p(u|s)
var speaker = function(obj){
  Infer({model: function(){
    // assume uniform utterance prior
    var utterance = uniformDraw(utterances)
    factor(alpha * // softmax is implicit (exp*log is just identity function)
           // utility function 
           (literalListener(utterance).score(obj)
                    - cost(utterance)))
    return utterance
  }})
}
///////////////////////////////



///// pragmatic listener /////

// pragmatic listener based on Bayes rule
var pragmaticListener = function(utterance){
  Infer({model: function(){
    var obj = objectPrior()  // prior
    observe(speaker(obj), utterance)  // lh
    return obj
  }})
}

viz.table(pragmaticListener("1"))

// unfold the following lines to see complete probability tables
///fold: 
var object_strings = map(function(obj) {return obj.string}, objects)
display("literal listener")
display(condProb2Table(literalListener, utterances, object_strings, 4))
display("")
display("speaker")
display(condProb2Table(speaker, object_strings, utterances, 2))
display("")
display("pragmatic listener")
display(condProb2Table(pragmaticListener, utterances, object_strings, 2))
///

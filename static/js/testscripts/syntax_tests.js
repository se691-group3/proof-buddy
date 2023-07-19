QUnit.test("Remove Justification with Just Symbol Test", function( assert ) { 

      //removeJustification() should return the substring before the '#'
      let str = 'A∧B #∧I, 1,2';
      let str2 = removeJustification(str);
      assert.equal(str2, 'A∧B ', "The initial string was " + str + " while the returned string is " + str2);
});

QUnit.test("Remove Justification without Just Symbol Test", function( assert ) { 

      //removeJustification should return the same string if there is no '#'
      let str = '(A∧B)∨C';
      let str2 = removeJustification(str);
      assert.equal(str2, '(A∧B)∨C', "The initial string was " + str + " while the returned string is " + str2);
});

QUnit.test("Has Valid Symbols with Valid Symbols Test", function( assert ) { 

      //hasValidSymbols() should return True if all characters in the string are valid TFL symbols
      var value = "A->B"; 
      var result = hasValidTFLSymbols(value);
      assert.true(result, "The expression " + value + " is valid!");
});

QUnit.test("Has Valid Symbols with Invalid Symbols Test", function( assert ) { 

      //hasValidSymbols() should return False if one or more characters in the string are not valid TFL symbols
      var value = "A>B=C"; 
      var result = hasValidTFLSymbols(value);
      assert.false(result, "The expression " + value + " is invalid!");
});

QUnit.test("Has Valid Symbols with Multiple Commas Test", function ( assert ) {

      //An input string that delimits clauses with commmas should be accepted
      let str = 'AvB,A→B,B→C';

      assert.true(hasValidTFLSymbols(str), "The expression " + str + " is valid!");

})

QUnit.test("Has Balanced Paranthesis Test with Balanced Paranthesis", function( assert ) {

      //hasBalancedParens should return True if all parentheses in the string are balanced and properly matching
      let str = '{[]{()}}';
      assert.true(hasBalancedParens(str), "The paranthesis of " + str + " are balanced.");
});

QUnit.test("Has Balanced Paranthesis Test with Unbalanced Paranthesis", function( assert ) {

      //hasBalancedParens should return False if parentheses in the string are unbalanced or not properly matching
      let str1 = '[{}{})(]'
      let str2 = '((()'
      let str3 = '(]'

      assert.false(hasBalancedParens(str1), "The paranthesis of " + str1 + " are NOT balanced.");
      assert.false(hasBalancedParens(str1), "The paranthesis of " + str2 + " are NOT balanced.");
      assert.false(hasBalancedParens(str1), "The paranthesis of " + str3 + " are NOT balanced.");
});

QUnit.test("Set Depth Array Test", function( assert ) {

      //The Set Depth Array function should successfully return depth arrays with values matching the a1 and a2 arrays 
      //that reflect the depth of the TFL characters for both expressions.

      let str = '(A∧B)∨C';
      let str2 = '[(A∧B)∨C]';
      let depth_array = setDepthArray(str);
      let depth_array_2 = setDepthArray(str2);
      let a1 = [1, 1, 1, 1, 0, 0, 0]; 
      let a2 = [1, 2, 2, 2, 2, 1, 1, 1, 0];

      assert.equal(JSON.stringify(depth_array), JSON.stringify(a1), "The sequence " + str + " has the expected depth values of " + JSON.stringify(a1));
      assert.equal(JSON.stringify(depth_array_2), JSON.stringify(a2), "The sequence " + str2 + " has the expected depth values of " + JSON.stringify(a2));
});

QUnit.test("Finding the Main Operator without Parenthesis Test 1", function( assert ) {
      
      //findMainOperator should return the main logical operator of a TFL statement

      let str = '(A∧B)∨C'
      assert.equal(findMainOperator(str), 5, "The main operator of " + str + "was found at " + findMainOperator(str));
});

QUnit.test("Finding the Main Operator without Parenthesis Test 2", function( assert ) {

      //findMainOperator should return the main logical operator of a TFL statement

      let str = '[(A∧B)∨C]';
      assert.equal(findMainOperator(str), 6, "The main operator of " + str + "was found at " + findMainOperator(str));
});

QUnit.test("Atomic Sentence Being Valid TFL Test", function( assert ) {

      //isValidTFL should return true if provided an atomic sentence
      let str1 = 'A';
      let str2 = 'Z';

      assert.equal(isValidTFL(str1), "This is a valid TFL statement.", "The atomic sentence " + str1 + " is a valid TFL sentence.");
      assert.equal(isValidTFL(str2), "This is a valid TFL statement.", "The atomic sentence " + str2 + " is a valid TFL sentence.");
});

QUnit.test("Well Formed Formulas with One Operator Being Valid TFL Input Test", function( assert ) {

      //isValidTFL should return true if provided a well-formed formula (WFF) with one operator
      let str1 = 'A∧B';
      let str2 = '(C∨D)';
      let str3 = '¬E';
      let str4 = '{X→Y}';
      let str5 = 'A↔Z';

     assert.equal(isValidTFL(str1), "This is a valid TFL statement.", "The well formed formula " + str1 + " is a valid TFL sentence."); 
     assert.equal(isValidTFL(str2), "This is a valid TFL statement.", "The well formed formula " + str2 + " is a valid TFL sentence.");
     assert.equal(isValidTFL(str3), "This is a valid TFL statement.", "The well formed formula " + str3 + " is a valid TFL sentence."); 
     assert.equal(isValidTFL(str4), "This is a valid TFL statement.", "The well formed formula " + str4 + " is a valid TFL sentence."); 
     assert.equal(isValidTFL(str5), "This is a valid TFL statement.", "The well formed formula " + str5 + " is a valid TFL sentence.");  
});

QUnit.test("Well Formed Formulas with Multiple Operators Being Valid TFL Input Test", function( assert ) {

      //isValidTFL should return true if provided a WFF with multiple operators

      let str1 = '(A∧B)∨C'
      let str2 = '(A∧B)∨[(¬C→D)∧(A↔Z)]'

      assert.equal(isValidTFL(str1), "This is a valid TFL statement.", "The well formed formula " + str1 + " is a valid TFL sentence.");
      assert.equal(isValidTFL(str2), "This is a valid TFL statement.", "The well formed formula " + str2 + " is a valid TFL sentence.");
});

QUnit.test("Is Valid TFL Against Invalid Input Test", function( assert ) {

      //isValidTFL should return false if provided with a string that does not conform to TFL sentence rules
      let invalid_symbols = 'A+Z';
      let unbalanced_parens = '[A∧B)]';

      assert.notEqual(isValidTFL(invalid_symbols), "This is a valid TFL statement.", "The string " + invalid_symbols + " is NOT a valid TFL sentence.");
      assert.notEqual(isValidTFL(unbalanced_parens), "This is a valid TFL statement.", "The string " + unbalanced_parens + " is NOT a valid TFL sentence.");
});
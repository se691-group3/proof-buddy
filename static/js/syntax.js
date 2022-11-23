/*
A Javascript equivalent to the current Syntax Python file that valid_input.js utilizes to check if the user's input is valid
*/

//TFL Syntax fields
const ATOMIC = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
'T', 'U', 'V', 'W', 'X', 'Y', 'Z'];
const TFL_BASIC_RULES = ['∧I','∧E','∨I','∨E','¬I','¬E','→I','→E','X','IP'];
const TFL_DERIVED_RULES = ['⊥I','⊥E','TND','↔I','↔E','DS','R','MT','DNE','DeM','Pr','Hyp','LEM'];


//FOL Syntax fields
const NAMES = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r'];
const VARS = ['s', 't', 'u', 'v', 'w', 'x', 'y', 'z'];
const PREDICATES = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z'];
const QUANTIFIERS = ['∀','∃','='];
const FOL_BASIC_RULES = ['∃I','∃E','∀I','∀E','=I','=E'];
const FOL_DERIVED_RULES = ['CQ'];

//General syntax
const CONNECTIVES = ['∧','∨','¬','→','→', '↔','^', '&','v','<','>','->','<->','-','~'];
const PARENS = ['(','[','{',')',']','}'];
const OPEN_PARENS=['(', '[', '{'];
const CLOSED_PARENS=[')', ']', '}'];
const DELIMITERS = [',',' ',';'];
const CONTRADICTION = ['⊥'];
const DOMAIN = ['∈'];
const ESCAPES = ["\\and","\\or","\\not","\\imp","\\iff","\\con","\\all","\\exi","\\in"];


function isValidTFL(string) {

    /*
    Determine if a line of text represents a valid TFL statement
    Lines in a `prooftext` contain a justification after the '#' symbol
    If the line contains a justification, remove it
    */
    let line = "";
    line = string;
    if(line.includes('#'))
    {
        removeJustification(line);
    }
    
    //Strip all whitespace from the line
    line.replace(/\s+/g, '');

    //Check if the string is a derived rule
    if(isLogicRule(line))
    {
        return "This is a valid TFL statement.";
    }

    //Verify all remaining characters are valid TFL symbols
    if(hasValidTFLSymbols(line))
    {
        //Check for matching parentheses
        if(hasBalancedParens(line))
        {
            //Determine the depth of each char in the line
            let depthArray = setDepthArray(line);

            // Remove matching outermost parentheses
            if(depthArray[0] == 1)
            {
                let parenthesesMatch = true;
                let index = 0;

                //Depth drops to zero somewhere if outermost parentheses do not match
                for(var i = 0; i < line.length-1; i++)
                {
                    parenthesesMatch = parenthesesMatch && (depthArray[index] > 0);
                    index++;
                }

                //Strip the outermost parentheses, call function recursively
                //Add one to the result for the leading parenthesis that was removed
                if(parenthesesMatch)
                {
                    return isValidTFL(line.substring(1, line.length-1));
                }

                //Find the main logical operator
                if (line.includes('∧') || line.includes('∨') || line.includes('¬') || line.includes('→') || line.includes('↔'))
                {
                    let operatorIndex = findMainOperator(line);

                    //Grab the substrings around the main operator
                    let left = line.substring(0, operatorIndex);
                    let right = line.substring(operatorIndex+1, line.length);

                    //There should be values on both sides unless the operator is ¬
                    if(line.charAt(operatorIndex) != '¬')
                    {
                        if(left == '')
                        {
                            return "The left side of the main logical operator (" + line.charAt(operatorIndex) + ") is empty!";
                            //return false;
                        }
                        if(right == '')
                        {
                            return "The right side of the main logical operator (" + line.charAt(operatorIndex) + ") is empty!";
                            //return false;
                        }
                    }

                    //Determine that both substrings are valid TFL sentences (recursion)
                    let leftIsValid = isValidTFL(left);
                    let rightIsValid = isValidTFL(right);

                    if(!(leftIsValid && rightIsValid))
                    {                       
                        let substringError = "";

                        if(!leftIsValid)
                        {
                            substringError = substringError + "The left substring of the main operator (" + line.charAt(operatorIndex) + ") is invalid! ";
                        }
                               
                        if(!rightIsValid)
                        {
                            substringError = substringError + "The right substring of the main operator (" + line.charAt(operatorIndex) + ") is invalid!";
                        }
                     
                        
                         
                        return substringError;
                    }
                }
            }    
        }            
        else{
            return "This statement does not have balanced parantheses." ;
        }
    }
    else{
        return "This statement has at least one invalid TFL symbol." ;
    }

    //If we reached this line, everything checks out

    return "This is a valid TFL statement.";

}

function isValidFOL(string){

    /***
     * Determine if a string is a valid FOL statement. 
     */

    let line = "";
    line = string;
    
    //If the string is a valid TFL statement, then it's automatically a valid FOL statement
    if(isValidTFL(line).includes("This is a valid TFL statement"))
    {
        return "This is a valid FOL statement.";
    }

    //Remove whitespace and jusitification

    if(line.includes('#'))
    {
        removeJustification(line);
    }
    
    //Strip all whitespace from the line
    line.replace(/\s+/g, '');

    //Check if the string is a derived rule
    if(isLogicRule(line))
    {
        return "This is a valid FOL statement.";
    }

    //Make sure all remaining characters are valid FOL symbols
    if(hasValidFOLSymbols(line))
    {
        //Next make sure the parenthesis/brackets are balanced
        if(hasBalancedParens(line))
        {
            //Determine the depth of each char in the line
            let depthArray = setDepthArray(line);

            // Remove matching outermost parentheses
            if(depthArray[0] == 1)
            {
                let parenthesesMatch = true;
                let index = 0;

                //Depth drops to zero somewhere if outermost parentheses do not match
                for(var i = 0; i < line.length-1; i++)
                {
                    parenthesesMatch = parenthesesMatch && (depthArray[index] > 0);
                    index++;
                }

                //Strip the outermost parentheses, call function recursively
                //Add one to the result for the leading parenthesis that was removed
                if(parenthesesMatch)
                {
                    return isValidFOL(line.substring(1, line.length-1));
                }

                //Find the main logical operator
                if (line.includes('∧') || line.includes('∨') || line.includes('¬') || line.includes('→') || line.includes('↔'))
                {
                    let operatorIndex = findMainOperator(line);

                    //Grab the substrings around the main operator
                    let left = line.substring(0, operatorIndex);
                    let right = line.substring(operatorIndex+1, line.length);

                    //There should be values on both sides unless the operator is ¬
                    if(line.charAt(operatorIndex) != '¬')
                    {
                        if(left == '')
                        {
                            return "The left side of the main logical operator (" + line.charAt(operatorIndex) + ") is empty!";
                            //return false;
                        }
                        if(right == '')
                        {
                            return "The right side of the main logical operator (" + line.charAt(operatorIndex) + ") is empty!";
                            //return false;
                        }
                    }

                    //Determine that both substrings are valid FOL sentences (recursion)
                    let leftIsValid = isValidFOL(left);
                    let rightIsValid = isValidFOL(right);

                    if(!(leftIsValid && rightIsValid))
                    {                       
                        let substringError = "";

                        if(!leftIsValid)
                        {
                            substringError = substringError + "The left substring of the main operator (" + line.charAt(operatorIndex) + ") is invalid! ";
                        }
                               
                        if(!rightIsValid)
                        {
                            substringError = substringError + "The right substring of the main operator (" + line.charAt(operatorIndex) + ") is invalid!";
                        }
                     
                        
                         
                        return substringError;
                    }
                }
            }
        }
        else{
            return "This statement does not have balanced parantheses.";
        }

    }
    else{
        return "This statement has at least one invalid FOL symbol.";
    }

    //If we reached this line, everything checks out
    return "This is a valid FOL statement.";

}

function removeJustification(string){
    //Removes the justification from the line, if present
    let line = "";
    line = string;

    let char = '#';
    if(line.includes(char))
    {
        let endIndex = line.indexOf(char);
        line = line.substring(0, endIndex);
    }

    return line;

}

function hasBalancedParens(string){
    //Determines if a string has balanced parentheses
    let stack = [];
    let line = "";
    line = string;

    for(var i = 0; i < line.length; i++)
    {
        if(OPEN_PARENS.includes(line.charAt(i)))
        {
            stack.push(line.charAt(i));
        }
        else if(CLOSED_PARENS.includes(line.charAt(i)))
        {
            let position = CLOSED_PARENS.indexOf(line.charAt(i));
            if(stack.length > 0 && OPEN_PARENS[position] == stack[stack.length - 1])
            {
                stack.pop();
            }
            else{
                return false;
            }
        }
    }

    if(stack.length == 0)
    {
        return true;
    }

    return false;

}

function hasValidTFLSymbols(string){

    let line = "";
    line = string;

    //Verifies that all characters in a string are valid TFL symbols
    for(var i = 0; i < line.length; i++)
    {
        if(!(ATOMIC.includes(line.charAt(i)) || CONNECTIVES.includes(line.charAt(i)) || PARENS.includes(line.charAt(i)) || DELIMITERS.includes(line.charAt(i)) || DOMAIN.includes(line.charAt(i)) || CONTRADICTION.includes(line.charAt(i))))
        {
            return false;
        }
    }

    return true;

}

function hasValidFOLSymbols(string){

    let line = "";
    line = string;

    //Verifies that all characters in a string are valid FOL symbols
    for(var i = 0; i < line.length; i++)
    {
        if(!(NAMES.includes(line.charAt(i)) || VARS.includes(line.charAt(i)) || PREDICATES.includes(line.charAt(i)) || QUANTIFIERS.includes(line.charAt(i)) || CONNECTIVES.includes(line.charAt(i)) || PARENS.includes(line.charAt(i)) || DOMAIN.includes(line.charAt(i)) || CONTRADICTION.includes(line.charAt(i)) || DELIMITERS.includes(line.charAt(i))))
        {
            return false;
        }
    }
    
    return true;
}

function findMainOperator(string){

    //Returns the index of the main logical operator in a TFL sentence
    let line = "";
    line = string;

    let operatorIndex = 0;

    //Determine the depth of each char in the sentence
    let depthArray = setDepthArray(line);

    //Remove matching outermost parentheses
    if(depthArray[0] == 1)
    {
        let parenthesesMatch = true;
        let index = 0;

        //Depth drops to zero somewhere if outermost parentheses do not match
        for(var i = 0; i < line.length-1; i++)
        {
            parenthesesMatch = (parenthesesMatch && depthArray[index] > 0);
            index++;
        }

        //Strip the outermost parentheses, call function recursively
        //Add one to the result for the leading parenthesis that was removed
        if(parenthesesMatch)
        {
            line = line.substring(1, line.length-1);
            return findMainOperator(line) + 1;
        }

    }

    //Find the main operator
    for(var i = 0; i < line.length; i++)
    {
        if(CONNECTIVES.includes(line.charAt(i)) && depthArray[operatorIndex] == 0)
        {
            return operatorIndex;
        }
        else{
            operatorIndex++;
        }

    }

    //If no operator found, return 0
    return 0;        


}

function setDepthArray(string){

    //Returns an array containing the depth of each character in a TFL sentence

    let depth = 0;
    let depthArray = [];

    let line = "";
    line = string;

    for(var i = 0; i < line.length; i++)
    {
        if(OPEN_PARENS.includes(line.charAt(i)))
        {
            depth++;
        }
        else if(CLOSED_PARENS.includes(line.charAt(i)))
        {
            depth--;
        }

        depthArray.push(depth);
    }

    return depthArray;
}

function isLogicRule(string){

    //If the string is a derived rule for FOL or TFL, then the syntax is valid.
    let line = string;
    for (var i = 0; i < TFL_BASIC_RULES.length; i++) {
        if (TFL_BASIC_RULES[i] == line) {
            return true;
        }
    }

    for (var i = 0; i < TFL_DERIVED_RULES.length; i++) {
        if (TFL_DERIVED_RULES[i] == line) {
            return true;
        }
    }

    for (var i = 0; i < FOL_BASIC_RULES.length; i++) {
        if (FOL_BASIC_RULES[i] == line) {
            return true;
        }
    }

    for (var i = 0; i < FOL_DERIVED_RULES.length; i++) {
        if (FOL_DERIVED_RULES[i] == line) {
            return true;
        }
    }


    return false;
}
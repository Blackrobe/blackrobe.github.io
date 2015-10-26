/* 
		function calculate(): Just to calculate total EXP needed from the current level to reach goal level.
		
		The EXP formula for each level is pretty simple:
		BASE_EXP + (n - BASE_LV) * (NEXT_EXP - BASE_EXP) + ((n - (BASE_LV + 1) + 1) * (n - (BASE_LV + 1)) / 2) * INCREMENT
		Level 51-58 follows the same constants.
		Level 58-255 follows a different constants.
		Level 255 and above (until when, I didn't know) follows an even different constants.
			
		To calculate from level 51 to level 58 you just need the same set of constants (NEXT_EXP, BASE_EXP, INCREMENT, and BASE_LV). But to calculate beyond level 58 you need a different constants (a new NEXT_EXP, BASE_EXP, INCREMENT, and BASE_LV) otherwise the result will be incorrect. The same goes with level 58 to level 255. Beyond level 255, the calculation uses a new and different constants than before.
	*/

	function calculate() {
			
		var currentLevel = parseInt(document.getElementById("currentLevel").value);
		var currentEXP = parseInt(document.getElementById("currentEXP").value);
		var goalLevel = parseInt(document.getElementById("goalLevel").value);
		var questEXP = parseInt(document.getElementById("questEXP").value);
			
		if (currentLevel != "0" && goalLevel != "0" && questEXP != "0") {		
			
			if (goalLevel < currentLevel) {
				document.getElementById("result").innerHTML = "Invalid: You can't level down.";
			}
			else if (currentLevel < 51 || currentLevel > 299 || goalLevel < 51 || goalLevel > 300) {
				document.getElementById("result").innerHTML = "Can only calculate from level 51 to 300.";
			}		
			else {
				
				function f(n) {
					if (n >= 51 && n < 58) {
						BASE_EXP = 19958;
						BASE_LV = 51;
						NEXT_EXP = 20636;
						INCREMENT = 6
						return BASE_EXP + (n - BASE_LV) * (NEXT_EXP - BASE_EXP) + ((n - (BASE_LV + 1) + 1) * (n - (BASE_LV + 1)) / 2) * INCREMENT
					}
					else if (n >= 58 && n < 255) {
						BASE_EXP = 24830
						BASE_LV = 58
						NEXT_EXP = 25580
						INCREMENT = 2
						return BASE_EXP + (n - BASE_LV) * (NEXT_EXP - BASE_EXP) + ((n - (BASE_LV + 1) + 1) * (n - (BASE_LV + 1)) / 2) * INCREMENT
					}
					else {
						BASE_EXP = 212713
						BASE_LV = 255
						NEXT_EXP = 214114
						INCREMENT = 3
						return BASE_EXP + (n - BASE_LV) * (NEXT_EXP - BASE_EXP) + ((n - (BASE_LV + 1) + 1) * (n - (BASE_LV + 1)) / 2) * INCREMENT
					}
				}
				
				goalEXP = 0;
				
				for (i = currentLevel; i < goalLevel; i++) {
					goalEXP = goalEXP + f(i);
				}				
				
				if (currentEXP == 0) {
					questCount = (goalEXP % questEXP == 0) ? Math.floor(goalEXP / questEXP) : Math.floor(goalEXP / questEXP)+ 1;
				}
				else {
					goalEXP = goalEXP - currentEXP;
					questCount = (goalEXP % questEXP == 0) ? Math.floor(goalEXP / questEXP) : Math.floor(goalEXP / questEXP)+ 1;
				}
				
                document.getElementById("result").innerHTML = "You have to run the quest<h3>" + questCount + "</h3>times to reach level " + goalLevel + ".";
                
				document.getElementById("goalEXPValue").value = goalEXP;
			}
		}
		
	}

	function showEXPTable() {
		function f(n) {
			if (n >= 51 && n < 58) {
				var BASE_EXP = 19958;
				var BASE_LV = 51;
				var NEXT_EXP = 20636;
				var INCREMENT = 6
				return BASE_EXP + (n - BASE_LV) * (NEXT_EXP - BASE_EXP) + ((n - (BASE_LV + 1) + 1) * (n - (BASE_LV + 1)) / 2) * INCREMENT
			}
			else if (n >= 58 && n < 255) {
				var BASE_EXP = 24830
				var BASE_LV = 58
				var NEXT_EXP = 25580
				var INCREMENT = 2
				return BASE_EXP + (n - BASE_LV) * (NEXT_EXP - BASE_EXP) + ((n - (BASE_LV + 1) + 1) * (n - (BASE_LV + 1)) / 2) * INCREMENT
			}
			else {
				var BASE_EXP = 212713
				var BASE_LV = 255
				var NEXT_EXP = 214114
				var INCREMENT = 3
				return BASE_EXP + (n - BASE_LV) * (NEXT_EXP - BASE_EXP) + ((n - (BASE_LV + 1) + 1) * (n - (BASE_LV + 1)) / 2) * INCREMENT
			}
		}
		
		resultText = "";
		totalEXP = 0;
		
		var currentLevel = parseInt(document.getElementById("currentLevel").value);		
		var goalLevel = parseInt(document.getElementById("goalLevel").value);
		
		for (i = currentLevel; i < goalLevel; i++) {
			resultText = resultText + "Level " + i + ": " + f(i) + " EXP required to level up." + "<br>";
			totalEXP = parseInt(totalEXP) + f(i);
		}
		
		document.getElementById("EXPTable").innerHTML = "";
        document.getElementById("EXPTable").innerHTML = resultText;
		document.getElementById("showEXPListButton").value = "Hide Details";
		document.getElementById("showEXPListButton").onclick = function() { hideEXPTable(); };
	}

	function hideEXPTable() {
		document.getElementById("showEXPListButton").value = "Show Details";
		document.getElementById("showEXPListButton").onclick = function() { showEXPTable(); };
	}

	function calculateTime() {
	
		var currentLevel = parseInt(document.getElementById("currentLevel").value);
		var currentEXP = parseInt(document.getElementById("currentEXP").value);
		var goalLevel = parseInt(document.getElementById("goalLevel").value);
		var questEXP = parseInt(document.getElementById("questEXP").value);
		var questEnergy = parseInt(document.getElementById("questEnergy").value);
		var questTime = parseInt(document.getElementById("questTime").value);
	
		function f(n) {
			if (n >= 51 && n < 58) {
				BASE_EXP = 19958;
				BASE_LV = 51;
				NEXT_EXP = 20636;
				INCREMENT = 6
				return BASE_EXP + (n - BASE_LV) * (NEXT_EXP - BASE_EXP) + ((n - (BASE_LV + 1) + 1) * (n - (BASE_LV + 1)) / 2) * INCREMENT
			}
			else if (n >= 58 && n < 255) {
				BASE_EXP = 24830
				BASE_LV = 58
				NEXT_EXP = 25580
				INCREMENT = 2
				return BASE_EXP + (n - BASE_LV) * (NEXT_EXP - BASE_EXP) + ((n - (BASE_LV + 1) + 1) * (n - (BASE_LV + 1)) / 2) * INCREMENT
			}
			else {
				BASE_EXP = 212713
				BASE_LV = 255
				NEXT_EXP = 214114
				INCREMENT = 3
				return BASE_EXP + (n - BASE_LV) * (NEXT_EXP - BASE_EXP) + ((n - (BASE_LV + 1) + 1) * (n - (BASE_LV + 1)) / 2) * INCREMENT
			}
		}
				
		function g(n) {
			if (n >= 51 && n < 83)
				return 52 + Math.floor((n - 51 + 1) / 3) + 5 * Math.floor((n - 46 + 1) / 10)
			if (n >= 83 && n < 101)
				return 78 + Math.floor((n - 83) / 2) + 5 * Math.floor((n - 83 + 8) / 10)
			if (n >= 101 && n < 152)
				return 97 + Math.floor((n - 101) / 3)
			if (n >= 152 && n < 251)
				return 115 + 2 * Math.floor((n - 152) / 3)
			else
				return 180 + Math.floor((n - 251) / 3)
		}		
		
		totalTime = 0;
		
		resultTextEnergy = "";
		
		for (i = currentLevel; i < goalLevel; i++) {		
			
			neededEXP                  = f(i) - currentEXP;		
			numberOfTimes              = Math.floor(neededEXP/questEXP) + 1;
			howManyQuestWithFullEnergy = Math.floor(g(i) / questEnergy);
			cutEXP                     = (questEXP * numberOfTimes) - neededEXP;
			
			runningQuestTime = 0;
			waitEnergyTime = 0;
			
			if (numberOfTimes - howManyQuestWithFullEnergy > 0) {
				
				waitEnergyTime = ((numberOfTimes - howManyQuestWithFullEnergy) * questEnergy - (g(i) % questEnergy)) * 3;
				
				waitTime = ((numberOfTimes - howManyQuestWithFullEnergy) * questEnergy - (g(i) % questEnergy)) * 3 - howManyQuestWithFullEnergy * questTime;
				
				if (waitTime > 0) {
					resultTextEnergy = resultTextEnergy + "Level " + i + " : " + g(i) + " energy with current EXP: " + currentEXP + " --- EXP to level up: " + neededEXP + ". You need to run the quest " + numberOfTimes + " times to level up. You can run the quest " + howManyQuestWithFullEnergy + " times (will take you " + (howManyQuestWithFullEnergy * questTime) + " minutes) before you have to wait a total of " + waitTime + " minutes to do " + (numberOfTimes - howManyQuestWithFullEnergy) + " more.<br>";
				}
				else {
					waitEnergyTime = 0;
					runningQuestTime = numberOfTimes * questTime;
					
					resultTextEnergy = resultTextEnergy + "Level " + i + " : " + g(i) + " energy with current EXP: " + currentEXP + " --- EXP to level up: " + neededEXP + ". You need to run the quest " + numberOfTimes + " times. You can run the quest " + Math.floor(g(i) / questEnergy) + " times with that full energy (will take you " + (howManyQuestWithFullEnergy * questTime) + " minutes) and when you're done, you will have regenerated " + Math.floor((howManyQuestWithFullEnergy * questTime)/3) + " more energy to run the quest " + (numberOfTimes - howManyQuestWithFullEnergy) + " more times to level up.<br>";
				}
				
			}
			else {				
				runningQuestTime = numberOfTimes * questTime;	
				resultTextEnergy = resultTextEnergy + "Level " + i + " : " + g(i) + " energy with current EXP: " + currentEXP + " --- EXP to level up: " + neededEXP + ". You need to run the quest " + numberOfTimes + " times to level up.<br>";
			}
			
			totalTime = totalTime + runningQuestTime + waitEnergyTime;
			
			currentEXP = cutEXP;
		}				
				
		totalTimeText = "";
		
		if (totalTime >= 1440) {
			totalTimeText = Math.floor(totalTime/1440) + " day(s)";
			totalTime = totalTime % 1440;
			if (totalTime >= 60) {
				totalTimeText = totalTimeText + ", " + Math.floor(totalTime/60) + " hour(s)";
				totalTime = totalTime % 60;
				if (totalTime > 0) {
					totalTimeText = totalTimeText + ", " + totalTime + " minute(s)";
				}
			}				
		}
		else if (totalTime >= 60) {
			totalTimeText = Math.floor(totalTime/60) + " hour(s)";
			totalTime = totalTime % 60;
			if (totalTime > 0) {
				totalTimeText = totalTimeText + ", " + totalTime + " minute(s)";
			}
		}
		else {
			totalTimeText = totalTime + " minutes";
		}
		
		document.getElementById("resultEnergy").innerHTML = "About " + totalTimeText + "<br>";
		document.getElementById("resultEnergyDetails").innerHTML = resultTextEnergy;
	}
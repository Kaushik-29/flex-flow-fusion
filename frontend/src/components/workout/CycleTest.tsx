import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { calculateCycles, getRepsInCurrentCycle, getRepsToNextCycle, isCycleComplete, getExerciseConfig } from "@/lib/exercise-config";

export const CycleTest = () => {
  const [repCount, setRepCount] = useState(0);
  const [exercise, setExercise] = useState("squat");

  const cycles = calculateCycles(repCount, exercise);
  const repsInCurrentCycle = getRepsInCurrentCycle(repCount, exercise);
  const repsToNextCycle = getRepsToNextCycle(repCount, exercise);
  const config = getExerciseConfig(exercise);
  const cycleComplete = isCycleComplete(repCount, exercise);

  const addRep = () => {
    setRepCount(prev => prev + 1);
  };

  const resetReps = () => {
    setRepCount(0);
  };

  return (
    <div className="space-y-4 p-4">
      <Card>
        <CardHeader>
          <CardTitle>Cycle Tracking Test</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex space-x-2">
            <Button onClick={addRep}>Add Rep</Button>
            <Button variant="outline" onClick={resetReps}>Reset</Button>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <h3 className="font-semibold">Current Exercise: {exercise}</h3>
              <p>Reps per cycle: {config.reps_per_cycle}</p>
              <p>Points per cycle: {config.points_per_cycle}</p>
            </div>
            
            <div>
              <h3 className="font-semibold">Stats</h3>
              <p>Total Reps: {repCount}</p>
              <p>Completed Cycles: {cycles}</p>
              <p>Reps in current cycle: {repsInCurrentCycle}</p>
              <p>Reps to next cycle: {repsToNextCycle}</p>
              <p>Cycle complete: {cycleComplete ? "Yes" : "No"}</p>
            </div>
          </div>
          
          <div className="space-y-2">
            <h3 className="font-semibold">Test Different Exercises:</h3>
            <div className="flex flex-wrap gap-2">
              {["squat", "push-up", "jumping jack", "plank", "burpee"].map((ex) => (
                <Button
                  key={ex}
                  variant={exercise === ex ? "default" : "outline"}
                  size="sm"
                  onClick={() => setExercise(ex)}
                >
                  {ex}
                </Button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}; 
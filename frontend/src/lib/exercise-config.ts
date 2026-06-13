// Exercise configurations with reps per cycle
export const EXERCISE_CONFIGS = {
  "squat": { reps_per_cycle: 15, points_per_cycle: 15 },
  "push-up": { reps_per_cycle: 10, points_per_cycle: 10 },
  "forward lunge": { reps_per_cycle: 12, points_per_cycle: 12 },
  "side lunge": { reps_per_cycle: 12, points_per_cycle: 12 },
  "jumping jack": { reps_per_cycle: 20, points_per_cycle: 20 },
  "plank": { reps_per_cycle: 5, points_per_cycle: 15 }, // 5 reps = 3 seconds each
  "mountain climber": { reps_per_cycle: 15, points_per_cycle: 15 },
  "high knees": { reps_per_cycle: 20, points_per_cycle: 20 },
  "burpee": { reps_per_cycle: 8, points_per_cycle: 16 }, // Burpees worth more points
  "jump squat": { reps_per_cycle: 12, points_per_cycle: 18 } // Jump squats worth more points
};

export const getExerciseConfig = (exercise: string) => {
  const exerciseLower = exercise.toLowerCase();
  return EXERCISE_CONFIGS[exerciseLower as keyof typeof EXERCISE_CONFIGS] || { reps_per_cycle: 15, points_per_cycle: 15 };
};

export const calculateCycles = (reps: number, exercise: string) => {
  const config = getExerciseConfig(exercise);
  return Math.floor(reps / config.reps_per_cycle);
};

export const getRepsInCurrentCycle = (reps: number, exercise: string) => {
  const config = getExerciseConfig(exercise);
  return reps % config.reps_per_cycle;
};

export const getRepsToNextCycle = (reps: number, exercise: string) => {
  const config = getExerciseConfig(exercise);
  const repsInCurrentCycle = reps % config.reps_per_cycle;
  return config.reps_per_cycle - repsInCurrentCycle;
};

export const isCycleComplete = (reps: number, exercise: string) => {
  const config = getExerciseConfig(exercise);
  return reps > 0 && reps % config.reps_per_cycle === 0;
}; 
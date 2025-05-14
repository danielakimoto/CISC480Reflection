let video;
let handPose;
let hands = [];
let osc;
let playing = false;

const waveform = ["sine", "saw", "square", "triangle"];
const diatonic = [
    27.5, 30.87, 32.7, 36.71, 41.2, 43.65, 49.0, 55.0, 61.4, 65.41, 73.42, 82.41, 
    87.31, 98.00, 110.00, 123.47, 130.81, 146.83, 164.81, 174.61, 196.00, 220.00, 
    246.94, 261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25, 
    587.33, 659.25, 698.46, 783.99, 880.00, 987.77, 1046.50, 1174.66, 1318.51, 
    1396.91, 1567.98, 1760.00, 1975.53, 2093.00, 2349.32, 2637.02, 2793.83, 
    3135.96, 3520.00, 3951.07, 4186.01, 4698.64, 5274.04, 5587.65, 6271.93, 
    7040.00
];

const pentatonic = [
    27.5, 30.87, 34.65, 41.2, 46.25, // First octave
    55.0, 61.74, 69.3, 82.41, 92.5,  // Second octave
    110.0, 123.47, 138.59, 164.81, 185.0, // Third octave
    220.0, 246.94, 277.18, 329.63, 370.0, // Fourth octave
    440.0, 493.88, 554.37, 659.25, 740.0, // Fifth octave
    880.0, 987.77, 1108.73, 1318.51, 1480.0, // Sixth octave
    1760.0, 1975.53, 2217.46, 2637.02, 2960.0, // Seventh octave
    3520.0, 3951.07, 4434.92, 5274.04, 5920.0  // Eighth octave
];

let currentScale = diatonic; // Default scale
let note_x;
let startButton;
let scaleSelector;

function preload() {
    handPose = ml5.handPose({ flipped: true });
}

function setup() {
    createCanvas(windowWidth, windowHeight);

    // Initialize video
    video = createCapture(VIDEO, { flipped: true });
    video.size(width, height);
    video.hide();

    // Start hand pose detection
    handPose.detectStart(video, gotHands);

    // Create the oscillator but do not start it yet
    osc = new p5.Oscillator(waveform[0]);
    osc.amp(0); // Set amplitude to 0 initially

    note_x = width / currentScale.length;

    // Create the Start button
    startButton = createButton("Start Theremin");
    startButton.position(width / 2 - 50, height / 2 - 30); // Center the button
    startButton.mousePressed(startAudio);

    // Create the scale selector
    scaleSelector = createSelect();
    scaleSelector.position(width / 2 - 50, 25);
    scaleSelector.option("Diatonic");
    scaleSelector.option("Pentatonic");
    scaleSelector.changed(changeScale);
}

function startAudio() {
    // Start the audio context and the oscillator
    userStartAudio(); // Unlock the AudioContext
    osc.start();
    playing = true;

    // Remove the start button after starting
    startButton.remove();
}

function changeScale() {
    // Switch between diatonic and pentatonic based on selection
    let selectedScale = scaleSelector.value();
    currentScale = selectedScale === "Pentatonic" ? pentatonic : diatonic;

    // Update note spacing based on the new scale
    note_x = width / currentScale.length;
}

function draw() {
    background(0);

    // Display video
    image(video, 0, 0, width, height);


    // Process hand tracking data
    if (hands.length > 0) {
        let leftHand = null;
        let rightHand = null;

        for (let hand of hands) {
            if (hand.confidence > 0.1) {
                if (hand.handedness === "Left") leftHand = hand;
                if (hand.handedness === "Right") rightHand = hand;

                // Draw only the pointer finger (keypoint 8)
                let keypoint = hand.keypoints[8]; // Pointer finger keypoint
                if (hand.handedness === "Left") fill(255, 0, 255);
                else fill(255, 255, 0);
                noStroke();
                circle(keypoint.x, keypoint.y, 16); // Draw a circle at pointer finger position
            }
        }


        // Right hand controls pitch
        if (rightHand) {
            let rightX = rightHand.keypoints[8].x; // Pointer finger tip (keypoint 8)
            let note_pos = floor(rightX / note_x);
            let f = currentScale[constrain(note_pos, 0, currentScale.length - 1)];
            osc.freq(f);
        }

        // Left hand controls volume
        if (leftHand) {
            let leftY = leftHand.keypoints[8].y; // Pointer finger tip (keypoint 8)
            let a = map(leftY, 0, height, 1, 0, true);
            osc.amp(a);
        }
    } else {
        osc.amp(0); // Remove volume if no hands are detected
    }
}

function gotHands(results) {
    hands = results;
}

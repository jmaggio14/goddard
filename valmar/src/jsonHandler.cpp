/**
* Copyright (c) 2016, Jeffrey Maggio and Joseph Bartelmo
* 
* Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
* associated documentation files (the "Software"), to deal in the Software without restriction,
* including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
* and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
* subject to the following conditions:
* 
* The above copyright notice and this permission notice shall be included in all copies or substantial 
* portions of the Software.
* 
* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
* LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
* IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
* LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
* WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

*/
#if !defined JSON_SETTINGS
    #define JSON_SETTINGS
    #include "jsonHandler.hpp"
    #define JSON_LOAD_ATTEMPT 10
#endif

bool JsonSettings::isEnabled() {
    return enabled;
}

int JsonSettings::getIBeamOffset() {
    return ibeam_offset;
}

void JsonSettings::setIBeamOffset(int offset) {
    ibeam_offset = offset;
}

int JsonSettings::getFrameRate() {
    return framerate;
}

int JsonSettings::getExposureTime() {
    return exposure_us;
}

int JsonSettings::getGain() {
    return gain;
}

double JsonSettings::getGammaLuminosity() {
    return gamma_y;
}

double JsonSettings::getSharpness() {
    return sharpness;
}

int JsonSettings::getThreshold() {
    return threshold;
}

int JsonSettings::getHistogramMax() {
    return histogramMax;
}

int JsonSettings::getRefreshInterval() {
    return refresh_interval;
}

//getsCameraSerialNumber
char* JsonSettings::getCamera(const char* camera) {
    //ximeas api wants a char* not a const char* :(
    const char* cam;
    if (strcmp(camera, "left") == 0) {
        cam = left.c_str();
    }
    else if (strcmp(camera, "right") == 0) {
        cam = right.c_str();
    }
    char* charConversion = new char[strlen(cam) + 1];
    if (charConversion) {
        strcpy(charConversion, cam);
    }
    return charConversion; 
}

void JsonSettings::refreshAllData(string filename) {
    json settings;
    int attempt;    
    for(attempt = 0; attempt < JSON_LOAD_ATTEMPT; attempt++) {
        try {
            printf("Attempting to load in file %s\n", filename.c_str());
            std::ifstream t(filename);
            std::stringstream buffer;
            buffer << t.rdbuf();
            settings = json::parse(buffer.str());
            break;
        } catch (int i) { cvWaitKey(200); }
        if (attempt >= JSON_LOAD_ATTEMPT -1) {
            printf("Could not load settings, inuse?\n");
            return;
        }
    }
    enabled = settings["command"]["enabled"];
    refresh_interval = settings["command"]["refresh_frame_interval"];
    
    framerate = settings["capture"]["framerate"];
    exposure_us = settings["capture"]["exposure_us"];
    gain = settings["capture"]["gain"];
    gamma_y = settings["capture"]["gamma_y"];
    sharpness = settings["capture"]["sharpness"];

    image_queue_size = settings["system"]["image_queue_size"];

    threshold = settings["processing"]["threshold"];
    histogramMax = settings["processing"]["histogram_max"];

    write_location = settings["calibration"]["write_location"];
    pixel_ratio = settings["calibration"]["pixel_ratio"];

    left = settings["ximea_cameras"]["left"];
    right = settings["ximea_cameras"]["right"];

    //dont reload ibeam offset, that's subject to change 
}


# Smart Automation System - Usage Guide

## 🎯 Overview

The Smart Automation System is a powerful desktop automation tool that allows you to automate repetitive computer operations with precision and ease. This guide will help you understand and use all the features effectively.

## ✨ Main Features

### 1. **Button (Click)** - Simple Click Operations
- Click on any position on the screen
- Perfect for buttons, links, and interactive elements
- Uses precise coordinates for accurate clicking

### 2. **Input Box (Text Input)** - Text Entry
- Automatically type text at specified locations
- Ideal for form filling, login credentials, and data entry
- Supports any text content

### 3. **Text Area (Monitor Text)** - Text Monitoring
- Monitor specific areas for text changes
- Uses OCR (Optical Character Recognition) to read screen text
- Detect when specific text appears or disappears

### 4. **Image Area (Monitor Image)** - Image Monitoring
- Monitor areas for image changes
- Use template matching to detect specific images
- Perfect for detecting buttons, icons, or visual elements

### 5. **Custom Area (Click)** - Advanced Click Operations
- Click with custom coordinates
- Add delays before clicking
- Support complex click sequences

## 🚀 Getting Started

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# For text monitoring (OCR), also install Tesseract:
# macOS: brew install tesseract
# Windows: Download and install Tesseract from GitHub
# Linux: sudo apt-get install tesseract-ocr
```

### Launch the System
```bash
python3 smart_automation.py
```

## 📋 Step-by-Step Usage

### 1. **Adding Elements**
1. Click "➕ Add Element" button
2. Select the element type from the dropdown
3. Enter parameters (if required)
4. Click "🎯 Select Element"
5. Move your mouse to the target position
6. Confirm the selection

### 2. **Creating Automation Sequences**
1. Add multiple elements in the desired order
2. Review the element list
3. Click "▶️ Start Automation" to execute
4. Monitor the execution log for progress

### 3. **Stopping Automation**
- Click "⏹️ Stop" to halt execution
- The system will safely stop at the current step

## 🎯 Detailed Feature Guide

### **Text Area (Monitor Text) - OCR Text Monitoring**

**What it does:**
- Captures a screenshot of a selected rectangular area
- Uses OCR to extract text from the image
- Searches for specified text within the extracted content

**How to use:**
1. Select "Text Area (Monitor Text)"
2. Enter the text to search for (e.g., "Login", "Submit", "Error")
3. **Select a rectangular area:**
   - First, move mouse to TOP-LEFT corner of the area
   - Wait 3 seconds for the system to record this position
   - Then move mouse to BOTTOM-RIGHT corner of the area
   - Wait 3 seconds for the system to record the second position
4. The system will report if the text is found in the selected area

**Parameter examples:**
- `Login` - Search for "Login" text
- `Submit` - Search for "Submit" text
- `Error` - Search for "Error" text

**Real-world applications:**
- Wait for web pages to load completely
- Confirm successful operations
- Monitor for error messages
- Detect when specific content appears

### **Image Area (Monitor Image) - Image Detection**

**What it does:**
- Captures a screenshot of a selected rectangular area
- Compares it with a target image (if provided)
- Reports similarity match percentage

**How to use:**
1. Select "Image Area (Monitor Image)"
2. Enter target image filename (e.g., "button.png", "icon.jpg")
3. **Select a rectangular area:**
   - First, move mouse to TOP-LEFT corner of the area
   - Wait 3 seconds for the system to record this position
   - Then move mouse to BOTTOM-RIGHT corner of the area
   - Wait 3 seconds for the system to record the second position
4. System will report match confidence

**Parameter examples:**
- `button.png` - Match against button.png
- `icon.jpg` - Match against icon.jpg
- Leave empty - Just monitor area for changes

**Real-world applications:**
- Detect when buttons appear
- Monitor icon changes
- Wait for specific images to load
- Verify visual elements are present

### **Custom Area (Click) - Advanced Clicking**

**What it does:**
- Provides flexible clicking options
- Supports custom coordinates
- Allows timing control

**How to use:**

**Method 1: Select Position**
1. Select "Custom Area (Click)"
2. Leave parameter empty or enter "wait:2"
3. Choose position with mouse
4. System clicks selected position

**Method 2: Custom Coordinates**
1. Select "Custom Area (Click)"
2. Enter coordinates (e.g., "100,200")
3. System clicks specified X=100, Y=200 position

**Parameter examples:**
- `100,200` - Click at coordinates (100,200)
- `wait:2` - Wait 2 seconds then click selected position
- `500,300,wait:1` - Click (500,300) and wait 1 second

**Real-world applications:**
- Click dynamic elements
- Execute complex click sequences
- Add custom timing between actions
- Handle elements that change position

## 🔧 Advanced Usage Examples

### **Automated Login Process**
```
1. Input Box: Enter username
2. Input Box: Enter password
3. Custom Area: Click login button
4. Monitor Text: Wait for "Welcome" text
5. Monitor Image: Detect user avatar loaded
```

### **Form Filling Automation**
```
1. Input Box: Enter name
2. Input Box: Enter email
3. Custom Area: Click "Next" button
4. Monitor Text: Wait for "Step 2" to appear
5. Input Box: Enter phone number
6. Custom Area: Click "Submit" button
```

### **Website Testing**
```
1. Custom Area: Click navigation menu
2. Monitor Text: Wait for page title
3. Input Box: Enter search term
4. Custom Area: Click search button
5. Monitor Image: Detect search results
```

## ⚙️ Configuration Tips

### **Timing Considerations**
- Add appropriate delays between actions
- Consider page loading times
- Account for network latency

### **Error Handling**
- Monitor for error messages
- Add fallback actions
- Use try-catch logic in sequences

### **Precision Settings**
- Use precise coordinates for critical elements
- Test automation on different screen resolutions
- Consider UI scaling factors

## ⚠️ Important Notes

### **Dependencies**
- **OCR Functionality**: Requires Tesseract installation
- **Image Processing**: Requires OpenCV
- **Screen Access**: System needs screen capture permissions

### **Best Practices**
1. **Test First**: Always test automation on a small scale
2. **Backup Data**: Ensure important data is backed up
3. **Monitor Execution**: Watch the first few runs carefully
4. **Error Handling**: Include error detection in sequences
5. **Documentation**: Keep notes of successful sequences

### **Limitations**
- Screen resolution changes may affect coordinates
- Dynamic content may require adjustments
- Network-dependent operations may need retry logic
- OCR accuracy depends on text clarity

## 🛠️ Troubleshooting

### **Common Issues**

**OCR Not Working:**
```bash
# Install Tesseract
# macOS
brew install tesseract

# Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki

# Linux
sudo apt-get install tesseract-ocr
```

**Image Matching Issues:**
- Ensure target images are clear and distinctive
- Check image format (PNG, JPG supported)
- Verify image file paths are correct

**Click Accuracy Problems:**
- Use precise coordinates
- Consider screen scaling
- Test on target resolution

### **Performance Optimization**
- Use appropriate wait times
- Minimize unnecessary screenshots
- Optimize image sizes for matching

## 📚 Additional Resources

### **File Structure**
```
Smart-Automation-System/
├── smart_automation.py          # Main automation system
├── original_precise_selector.py # Precise element selector
├── start_smart.py              # Quick start script
├── requirements.txt            # Dependencies
├── README.md                   # Project overview
└── USAGE_GUIDE.md             # This guide
```

### **Log Files**
- Automation logs are saved in the `logs/` directory
- Check logs for debugging and optimization
- Logs include timestamps and detailed information

## 🎯 Success Tips

1. **Start Simple**: Begin with basic click and input operations
2. **Build Gradually**: Add complexity step by step
3. **Test Thoroughly**: Verify each step works before proceeding
4. **Document Everything**: Keep records of working sequences
5. **Stay Updated**: Keep dependencies current

---

**Happy Automating!** 🚀✨

For support and updates, check the project repository and documentation. 
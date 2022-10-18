/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package webscrapper;

import java.util.HashMap;
import java.util.Map;
import javax.swing.JTextArea;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;



/**
 *
 * @author Master01
 */

public class Scrapper extends Thread {
    /**
     * Clase que se dedicará a 
     */
    
    // Variables para los drivers 
    private String path_to_chromedriver = "C:\\Users\\Usuario\\Desktop\\TFG\\app\\app\\drivers\\chromedriver.exe";
    private boolean visible;
    private String item;
    private javax.swing.JTextArea textArea;

    public String getPath_to_chromedriver() {
        return path_to_chromedriver;
    }

    public void setPath_to_chromedriver(String path_to_chromedriver) {
        this.path_to_chromedriver = path_to_chromedriver;
    }

    public boolean isVisible() {
        return visible;
    }

    public void setVisible(boolean visible) {
        this.visible = visible;
    }

    public String getItem() {
        return item;
    }

    public void setItem(String item) {
        this.item = item;
    }

    public JTextArea getTextArea() {
        return textArea;
    }

    public void setTextArea(JTextArea textArea) {
        this.textArea = textArea;
    }



    public Scrapper(boolean visible, String item, javax.swing.JTextArea textArea) {
        this.visible = visible;
        this.item = item;
        this.textArea = textArea;
    }
    
    public WebDriver generarDriver() {
        System.setProperty("webdriver.chrome.driver",getPath_to_chromedriver());
        
        // Asginar a nulo para poder retornar 
        WebDriver driver = null;
        if (this.visible == false){
            Map prefs = new HashMap();
            prefs.put("profile.default_content_settings.cookies", 2);
            ChromeOptions options = new ChromeOptions();
            options.setExperimentalOption("prefs", prefs);
            options.addArguments("--headless");
            driver = new ChromeDriver(options);
        }
        else {
            Map prefs = new HashMap();
            prefs.put("profile.default_content_settings.cookies", 1);
            ChromeOptions options = new ChromeOptions();
            options.setExperimentalOption("prefs", prefs);
            driver = new ChromeDriver();
        }
        return driver; 

    }
    
    
    @Override
    public void run(){
        
    }
}

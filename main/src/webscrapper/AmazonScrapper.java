/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package webscrapper;


import java.io.IOException;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.lang.model.util.Elements;
import javax.swing.JTextArea;
import javax.swing.text.Document;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Element;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;

/**
 *
 * @author Master01
 */
public class AmazonScrapper extends Scrapper {

    public AmazonScrapper(boolean visible, String item, JTextArea textArea) {
        super(visible, item, textArea);
    }






   
    
    @Override
    public void run(){
        try {
            WebDriver driver = super.generarDriver();
            driver.get("https://amazon.com");
            
            WebElement searchbox = driver.findElement(By.id("twotabsearchtextbox"));
            WebElement searchButton = driver.findElement(By.id("nav-search-submit-button"));
            searchbox.sendKeys(super.getItem());
            searchButton.click();

            org.jsoup.nodes.Document doc = Jsoup.parse(driver.getPageSource());
            driver.quit();
            org.jsoup.select.Elements items = (org.jsoup.select.Elements) doc.getElementsByAttribute("data-index");
            String text = "";
            text = text + "AMAZON"+"\n"+"======================="+"\n";
            for (Element element : items) {
                System.out.println("Parseando html de amazon . . . .");
                org.jsoup.select.Elements element_titles = element.getElementsByClass("a-size-base-plus a-color-base a-text-normal");
                org.jsoup.select.Elements element_prices = element.getElementsByClass("a-price");
                
                if (element_titles.text().length() != 0){
                  text = text + (element_titles.text()) + "\n";                  
                } else if ((element_prices.text().length() != 0)){
                  text = text + (element_prices.text()) + "\n";
                  text = text + " " + "\n";
                } else if ((element_prices.text().length() == 0) && element_titles.text().length() != 0){
                  text = text + "Precio no disponible" + "\n";
                  text = text + " " + "\n";
                }

                // Reseteo las variables a null para evitar repetir elementos 
                element_titles = null;
                element_prices = null;
                

            }
            System.out.println(text); 
            super.getTextArea().setText(text);
               // driver.quit(); 


        } catch (Exception ex) {
            Logger.getLogger(AmazonScrapper.class.getName()).log(Level.SEVERE, null, ex);
            System.out.println("Excepción al correr AmazonScrapper");
        }
    }
}

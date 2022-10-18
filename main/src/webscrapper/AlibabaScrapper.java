/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package webscrapper;

import javax.swing.JTextArea;
import org.jsoup.select.Elements;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.jsoup.*;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;

/**
 *
 * @author Master01
 */
public class AlibabaScrapper extends Scrapper {

    public AlibabaScrapper(boolean visible, String item, JTextArea textArea) {
        super(visible, item, textArea);
    }
    


    @Override
    public void run(){
        WebDriver driver = super.generarDriver();
        driver.get("https://spanish.alibaba.com/");
        WebElement searchbox = driver.findElement(By.xpath("/html/body/div[1]/header/div[2]/div[3]/div/div[2]/form/div[2]/input"));
       
        if (super.isVisible()){
            // Rechazar cookies si el navegador es visible
            WebElement cookieBox = driver.findElement(By.xpath("/html/body/div[10]/div[2]/div/div[2]/div[2]"));
            cookieBox.click();
        }

        
        WebElement searchButton = driver.findElement(By.xpath("/html/body/div[1]/header/div[2]/div[3]/div/div[2]/form/i[1]"));
        searchbox.sendKeys(super.getItem());
        searchButton.click();
        Document doc = Jsoup.parse(driver.getPageSource());
        driver.quit();
        Elements items = (Elements) doc.getElementsByClass("list-no-v2-main__top-area");
        String text = "";
        text = text + "ALIBABA"+"\n"+"======================="+"\n";
        for (Element element : items) {
            System.out.println("Parseando html de alibaba . . . .");
            Elements element_titles = element.getElementsByClass("elements-title-normal__outter");
            Elements element_prices = element.getElementsByClass("organic-gallery-offer-section__price");
            text = text + (element_titles.text()) + "\n";
            text = text + (element_prices.text()) + "\n";
            text = text + " " + "\n";
            
        }
        System.out.println(text);
        super.getTextArea().setText(text);
            
    }
}

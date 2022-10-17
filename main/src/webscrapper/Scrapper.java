/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package webscrapper;



/**
 *
 * @author Master01
 */

public class Scrapper {
    /**
     * Clase que se dedicará a 
     */
    
    
    
    public Scrapper(){
    }

    public void inicializar_navegador() {
        WebDriver driver = new ChromeDriver();
        driver.get("https://amazon.com");
        driver.quit();
    }
}

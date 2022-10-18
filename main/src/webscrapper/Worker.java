/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package webscrapper;

import java.io.InputStream;
import java.io.OutputStream;
import java.util.ArrayList;

/**
 *
 * @author Master01
 */
public class Worker extends Process{
    
    private ArrayList<Scrapper> scrappers = new ArrayList<Scrapper>();
    
    public void initialise_scrappers(){
        for (int i = 0; i<scrappers.size(); i++){
            scrappers.get(i).start();
        }
        
    }
   
    public Worker(String item, boolean alibaba, boolean amazon, boolean visible,ArrayList<javax.swing.JTextArea> textAreas) {
        if (alibaba == true && amazon == false){
            AlibabaScrapper aliscrap = new AlibabaScrapper(visible,item,textAreas.get(0));
            scrappers.add(aliscrap);
        } else if (alibaba == false && amazon == true){
            AmazonScrapper amazscrap = new AmazonScrapper(visible,item,textAreas.get(1));
            scrappers.add(amazscrap);
            
        } else if (alibaba == true && amazon == true){
            AmazonScrapper amazscrap = new AmazonScrapper(visible,item,textAreas.get(0));
            AlibabaScrapper aliscrap = new AlibabaScrapper(visible,item,textAreas.get(1));
            scrappers.add(aliscrap);
            scrappers.add(amazscrap);
        } else {
            System.out.println("ERROR AL CONSTRUIR WORKER, DATOS ERRONEOS");
        }
    }
    
    
    // Overrides de clase Process
    @Override
    public OutputStream getOutputStream() {
        throw new UnsupportedOperationException("Not supported yet."); //To change body of generated methods, choose Tools | Templates.
    }

    @Override
    public InputStream getInputStream() {
        throw new UnsupportedOperationException("Not supported yet."); //To change body of generated methods, choose Tools | Templates.
    }

    @Override
    public InputStream getErrorStream() {
        throw new UnsupportedOperationException("Not supported yet."); //To change body of generated methods, choose Tools | Templates.
    }

    @Override
    public int waitFor() throws InterruptedException {
        throw new UnsupportedOperationException("Not supported yet."); //To change body of generated methods, choose Tools | Templates.
    }

    @Override
    public int exitValue() {
        throw new UnsupportedOperationException("Not supported yet."); //To change body of generated methods, choose Tools | Templates.
    }

    @Override
    public void destroy() {
        throw new UnsupportedOperationException("Not supported yet."); //To change body of generated methods, choose Tools | Templates.
    }
    
    
}

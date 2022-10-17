/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Main.java to edit this template
 */
package main;

import gui.LoginForm;
import webscrapper.Scrapper;

/**
 *
 * @author Master01
 */
public class Main {

    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) {
        // TODO code application logic here
       // LoginForm login = new LoginForm(); 
       // login.setVisible(true);
        Scrapper s = new Scrapper(); 
        s.inicializar_navegador();
        
        
    }
    
}

/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package bd;

import java.sql.Array;
import main.User;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.logging.Level;
import java.util.logging.Logger;
/**
 *
 * @author Usuario
 */
public class Conector {
    
    private final String url = "jdbc:postgresql://localhost:5432/tfg";
    private final String user = "postgres";
    private final String password = "Huev27POSTGRES";
    
   
    public Connection conectar() {
        Connection conn = null;
        try {
            conn = DriverManager.getConnection(url, user, password);
            System.out.println("Conectado a PostgreSQL.");
        } catch (SQLException e) {
            System.out.println(e.getMessage());
        }

        return conn;
    }
   public void anadir_usuario (User usuario){
        try {
            Connection conn = conectar();
            Statement statement = conn.createStatement();
            String SQL = ("INSERT INTO users(nombre,email,contrasena) "
                    + " VALUES (?,?,?);");
            PreparedStatement pstmt = conn.prepareStatement(SQL); {
                pstmt.setString(1, usuario.getNombre());
                pstmt.setString(2, usuario.getContrasena());
                pstmt.setString(3, usuario.getEmail());
            }
            pstmt.execute();
        } catch (SQLException ex) {
            Logger.getLogger(Conector.class.getName()).log(Level.SEVERE, null, ex);
        }
   }  
 
      public boolean comprobar_usuario (String nombre, String contrasena){
        boolean existe = false;
        try {
            Connection conn = conectar();
            String query = "SELECT * FROM users WHERE nombre like ? AND contrasena like ?;";
            PreparedStatement pstmt= conn.prepareStatement(query); {
                pstmt.setString(1, nombre);
                pstmt.setString(2,contrasena);
            }
            ResultSet rs = pstmt.executeQuery();
            if (!rs.isBeforeFirst() ) {    
                System.out.println("El usuario no existe"); 
                existe = false;
            } else if (rs.isBeforeFirst()){
                existe = true;
            }
        } catch (SQLException ex) {
            System.out.println(ex.getMessage());
        }
        return existe;
    }
}
      


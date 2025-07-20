# Ejemplo de uso de API Key (JWT) para generar imágenes desde Java

Este ejemplo muestra cómo consumir la API de generación de imágenes usando el token JWT que se obtiene en el área de perfil del frontend.

## Requisitos
- Java 8+
- Librería HTTP (por ejemplo, HttpURLConnection nativo o OkHttp)

## Ejemplo usando HttpURLConnection

```java
import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;

public class ImageGenApiExample {
    public static void main(String[] args) throws Exception {
        String apiUrl = "http://localhost:8000/api/generate-image"; // Cambia por tu endpoint real
        String jwtToken = "TU_TOKEN_JWT_AQUI"; // Pega aquí el JWT copiado del frontend

        String jsonInput = "{" +
            "\"prompt\": \"Un gato espacial con traje de astronauta\"," +
            "\"width\": 512," +
            "\"height\": 512" +
        "}";

        URL url = new URL(apiUrl);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("POST");
        conn.setRequestProperty("Content-Type", "application/json");
        conn.setRequestProperty("Authorization", "Bearer " + jwtToken);
        conn.setDoOutput(true);

        try (OutputStream os = conn.getOutputStream()) {
            byte[] input = jsonInput.getBytes("utf-8");
            os.write(input, 0, input.length);
        }

        int code = conn.getResponseCode();
        System.out.println("Código de respuesta: " + code);

        try (BufferedReader br = new BufferedReader(new InputStreamReader(conn.getInputStream(), "utf-8"))) {
            StringBuilder response = new StringBuilder();
            String line;
            while ((line = br.readLine()) != null) {
                response.append(line.trim());
            }
            System.out.println("Respuesta: " + response.toString());
        }
    }
}
```

## Notas
- Cambia `apiUrl` por la URL de tu backend.
- El JWT debe copiarse desde el área de perfil del frontend.
- El endpoint, parámetros y formato de respuesta pueden variar según tu API.



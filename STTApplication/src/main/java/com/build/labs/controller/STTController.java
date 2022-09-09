package com.build.labs.controller;

import java.io.IOException;
import java.io.InputStream;
import java.net.URISyntaxException;
import java.util.List;

import org.springframework.core.io.ClassPathResource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.multipart.MultipartFile;

import com.build.labs.services.STTService;

@Controller
public class STTController {
	
	private final STTService sttService;
	
	
	public STTController(STTService sttService) {
		super();
		this.sttService = sttService;
	}

	/*
	 * This method build the home page. This page can be accessible in different ways
	 * {"/", "", "/index", "/home"}, it returns the content in page index.html resides
	 * in src/main/resources/templates directory.
	 */
	@GetMapping({"/", "", "/index", "/home"})
    public String homepage() {
        return "index";
    }

	/*
	 * This method handles the file upload and convert it to a transcript and return the transcript
	 * to index page with model attribute result and if result holds any value
	 * index page displays the result.
	 */
	@PostMapping("/uploadFile")
	public String uploadFile(@RequestParam("file") MultipartFile multipartFile, Model model)
			throws IOException, URISyntaxException {
		String transcript = "File not found";
		try (InputStream inputStream = multipartFile.getInputStream()) {
			transcript = sttService.transcriptAudio(inputStream);
			
		} catch (IOException ioe) {
			throw new IOException("Could not upload file: ", ioe);
		}
		
		model.addAttribute("result", transcript);
		return "index";
	}
	
	
	@GetMapping("/transcript/{filename}")
	public String transcriptAudio(@PathVariable("filename") String filename, Model model) throws IOException, URISyntaxException {
		
		InputStream input = new ClassPathResource("static/audio/"+filename).getInputStream();
		String transcript = sttService.transcriptAudio(input);
		model.addAttribute("result", transcript);
		return "index";
	}
	
	@GetMapping("/transcript/{filename}/download")
    public ResponseEntity<String> download(@PathVariable("filename") String filename) throws IOException, URISyntaxException {

        HttpHeaders header = new HttpHeaders();
        header.add(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=output.json");
        header.add("Cache-Control", "no-cache, no-store, must-revalidate");
        header.add("Pragma", "no-cache");
        header.add("Expires", "0");

        
        InputStream input = readFile(filename);
        String transcript = sttService.transcriptAudio(input);
        
        return ResponseEntity.ok()
                .headers(header)
                .contentLength(transcript.length())
                .contentType(MediaType.parseMediaType("application/json"))
                .body(transcript);
    }
	
	@GetMapping("/transcript/all")
    public ResponseEntity<String> downloadAll() throws IOException, URISyntaxException {

        HttpHeaders header = new HttpHeaders();
        header.add(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=output.json");
        header.add("Cache-Control", "no-cache, no-store, must-revalidate");
        header.add("Pragma", "no-cache");
        header.add("Expires", "0");

        List<String> filenames = List.of("CallCenterSample1.mp3", "CallCenterSample2.mp3", "CallCenterSample3.mp3");
        
        String transcript = "---";
        
        for(String filename : filenames) {
        	 String output = sttService.transcriptAudio(readFile(filename));
        	 transcript = "File name: " + filename + "\n" + output;
        }
                
        return ResponseEntity.ok()
                .headers(header)
                .contentLength(transcript.length())
                .contentType(MediaType.parseMediaType("application/json"))
                .body(transcript);
    }
	
	private InputStream readFile(String filename) throws IOException {
		 return new ClassPathResource("static/audio/"+filename).getInputStream();
	}
	
}

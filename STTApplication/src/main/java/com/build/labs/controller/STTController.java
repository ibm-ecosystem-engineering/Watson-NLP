package com.build.labs.controller;

import java.io.IOException;
import java.io.InputStream;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.ui.Model;

import com.build.labs.services.STTService;

@Controller
public class FileUploadController {
	
	private final STTService sttService;
	
	
	public FileUploadController(STTService sttService) {
		super();
		this.sttService = sttService;
	}

	@GetMapping({"/", "", "/index", "/home"})
    public String homepage() {
        return "index";
    }

	@PostMapping("/uploadFile")
	public String uploadFile(@RequestParam("file") MultipartFile multipartFile, Model model)
			throws IOException {
		String transcript = "";
		try (InputStream inputStream = multipartFile.getInputStream()) {
			transcript = sttService.execute(inputStream);
			
		} catch (IOException ioe) {
			throw new IOException("Could not upload file: ", ioe);
		}
		
		model.addAttribute("result", transcript);
		return "index";
	}
}

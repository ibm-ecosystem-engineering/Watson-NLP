package com.build.labs.controllers;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PostMapping;

import com.build.labs.dto.CommonRequestDto;
import com.build.labs.services.CommonModelService;

@Controller
public class HomeController {
	
	private final CommonModelService commonService;

	public HomeController(CommonModelService commonService) {
		super();
		this.commonService = commonService;
	}
	
	@GetMapping({"/", "", "/index", "/home"})
    public String homepage(Model model) {
		model.addAttribute("commonRequest", new CommonRequestDto());
		model.addAttribute("result", "");
        return "index";
    }
	
	
	@PostMapping("/prediction")
    public String callIzumoModel(@ModelAttribute CommonRequestDto commonRequestDto, Model model){
		String result = commonService.predict(commonRequestDto);
		model.addAttribute("commonRequest", commonRequestDto);
		model.addAttribute("result", result);
		return "index";
	}

}

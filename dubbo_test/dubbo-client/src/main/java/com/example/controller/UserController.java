package com.example.controller;

import com.example.service.UserService;
import org.apache.dubbo.config.annotation.DubboReference;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class UserController {
    
    @DubboReference
    private UserService userService;
    
    @GetMapping("/user/{id}")
    public String getUserInfo(@PathVariable String id) {
        return userService.getUserInfo(id);
    }
}
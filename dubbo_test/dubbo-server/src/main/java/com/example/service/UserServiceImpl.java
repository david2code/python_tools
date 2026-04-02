package com.example.service;

import org.apache.dubbo.config.annotation.DubboService;

@DubboService
public class UserServiceImpl implements UserService {
    @Override
    public String getUserInfo(String userId) {
        return "User Info for ID: " + userId;
    }
}
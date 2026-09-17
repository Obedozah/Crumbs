# frontend
FROM node:22-alpine AS builder

# change to needed
WORKDIR /app

# node Modules???
# ENV PATH etc/etc/etc

# 'read' the packages
COPY package*.json ./

RUN npm install

COPY . .


# using node straight
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]


# nginx
# for later

# FROM nginx:alpine
# COPY --from=builder /app/dist /usr/share/nginx/html
# EXPOSE 80
# CMD ["nginx", "-g", "daemon off;"]
import { NextAuthOptions } from "next-auth";
import GithubProvider from "next-auth/providers/github";
import CredentialProvider from "next-auth/providers/credentials";
import axios from "axios";

export const authOptions: NextAuthOptions = {
  providers: [
    GithubProvider({
      clientId: process.env.GITHUB_ID ?? "",
      clientSecret: process.env.GITHUB_SECRET ?? "",
    }),
    CredentialProvider({
      id: "credentials",
      name: "Credentials",
      credentials: {
        email: {
          label: "email",
          type: "email",
          placeholder: "example@gmail.com",
        },
        password: {
          label: "password",
          type: "password"
        }
      },
      async authorize(credentials, req) {
        // for demo purposes
        if (credentials?.email === "demo@gmail.com") {
          return {"id": "demo", "name": "Demo User"};
        }
        const formData = new FormData();
        formData.append('username', credentials?.email ?? "");
        formData.append('password', credentials?.password ?? "");
        const response = await fetch('http://localhost:3001/api/v1/login', {
          method: 'POST',
          body: formData 
        });
        if (response.status !== 200) {
          // If you return null then an error will be displayed advising the user to check their details.
          return null;
        }
        const token = await response.json();
        if (token) {
          // Any object returned will be saved in `user` property of the JWT
          return {"id": token.access_token, "user": credentials?.email};
        } else {
          //Reject this callback with an Error thus the user will be sent to the error page with the error message as a query parameter
          throw new Error('Invalid credentials');
        }
      },
    }),
    CredentialProvider({
      id: "signup",
      name: "Signup",
      credentials: {
        email: {
          label: "email",
          type: "email",
        },
        password: {
          label: "password",
          type: "password"
        }
      },
      async authorize(credentials, req) {
        const response = await axios.post('http://localhost:3001/api/v1/users', {
          "username": credentials?.email,
          "password": credentials?.password
        });
        const { token } = response.data;
        if (token) {
          // Any object returned will be saved in `user` property of the JWT
          return {"id": token, "user": credentials?.email};
        } else {
          // If you return null then an error will be displayed advising the user to check their details.
          return null;

          // You can also Reject this callback with an Error thus the user will be sent to the error page with the error message as a query parameter
        }
      },
    }),

  ],
  pages: {
    signIn: "/login", //sigin page
  },
};

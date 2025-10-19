import { Button } from "./ui/button";
import { Card, CardContent } from "./ui/card";
import {
  ArrowRight,
  Users,
  Target,
  TrendingUp,
  Star,
  CheckCircle,
} from "lucide-react";
import { ImageWithFallback } from "./figma/ImageWithFallback";
import type { Page } from "../App";

interface LandingPageProps {
  onNavigate: (page: Page) => void;
  isAuthenticated?: boolean;
}

export function LandingPage({ onNavigate, isAuthenticated }: LandingPageProps) {
  return (
    <div className="min-h-screen">
      {/* Header */}
      <header
        className="border-b bg-white/95 backdrop-blur-sm sticky top-0 z-50"
        style={{ boxShadow: "0 2px 8px rgba(0,0,0,0.1)" }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div
              className="flex items-center space-x-2"
              style={{ cursor: "pointer" }}
              onClick={() =>
                onNavigate((!isAuthenticated ? "landing" : "dashboard") as Page)
              }
            >
              <div className="flex items-center justify-center">
                <ImageWithFallback
                  src="assets/logo.svg"
                  alt="Anblicks AI Career Coaching"
                />
              </div>
              <span className="text-xl font-semibold text-foreground">
                Anblicks Career Coach
              </span>
            </div>
            <nav className="hidden md:flex items-center space-x-8">
              <a
                href="#features"
                className="text-muted-foreground hover:text-foreground transition-colors"
              >
                Features
              </a>
              <a
                href="#testimonials"
                className="text-muted-foreground hover:text-foreground transition-colors"
              >
                Testimonials
              </a>
              {isAuthenticated ? (
                <Button onClick={() => onNavigate("dashboard")}>
                  Go to Dashboard
                </Button>
              ) : (
                <>
                  <Button variant="outline" onClick={() => onNavigate("login")}>
                    Login
                  </Button>
                  <Button onClick={() => onNavigate("registration")}>
                    Get Started
                  </Button>
                </>
              )}
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative py-20 lg:py-20 bg-gradient-to-br from-primary/5 via-accent/5 to-background">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-8">
              <div className="space-y-4">
                <h1 className="text-4xl lg:text-6xl font-bold text-foreground">
                  Shape Your Future with
                  <span className="text-primary"> AI Career Coach</span>
                </h1>
                <p className="text-xl text-muted-foreground max-w-xl">
                  Get personalized career guidance powered by AI. From
                  aspirations to actionable paths, we'll help you navigate your
                  professional journey with confidence.
                </p>
              </div>
              <div className="flex flex-col sm:flex-row gap-4">
                <Button
                  size="lg"
                  className="bg-primary hover:bg-primary/90"
                  onClick={() => onNavigate("registration")}
                >
                  Get Started <ArrowRight className="ml-2 w-5 h-5" />
                </Button>
              </div>
              <div className="flex items-center space-x-8 text-sm text-muted-foreground">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4 text-accent" />
                  <span>Free to start</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4 text-accent" />
                  <span>AI-powered guidance</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4 text-accent" />
                  <span>Personalized paths</span>
                </div>
              </div>
            </div>
            <div className="relative">
              <ImageWithFallback
                src="assets/image.png"
                alt="AI Career Coaching Illustration"
                className="w-full h-auto rounded-2xl shadow-2xl"
              />
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="features" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center space-y-4 mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-foreground">
              How It Works
            </h2>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
              Three simple steps to transform your career aspirations into
              actionable plans
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            <Card className="text-center p-4 border-2 hover:border-primary/20 transition-all">
              <CardContent className="space-y-4">
                <div className="w-16 h-16 bg-primary/10 rounded-2xl flex items-center justify-center mx-auto">
                  <Users className="w-8 h-8 text-primary" />
                </div>
                <h3 className="text-xl font-semibold">1. Register</h3>
                <p className="text-muted-foreground">
                  Tell us about your background, education, and career
                  aspirations
                </p>
              </CardContent>
            </Card>
            <Card className="text-center p-4 border-2 hover:border-primary/20 transition-all">
              <CardContent className="space-y-4">
                <div className="w-16 h-16 bg-accent/10 rounded-2xl flex items-center justify-center mx-auto">
                  <Target className="w-8 h-8 text-accent" />
                </div>
                <h3 className="text-xl font-semibold">2. Explore</h3>
                <p className="text-muted-foreground">
                  Get AI-powered career suggestions tailored to your goals and
                  interests
                </p>
              </CardContent>
            </Card>
            <Card className="text-center p-4 border-2 hover:border-primary/20 transition-all">
              <CardContent className="space-y-4">
                <div className="w-16 h-16 bg-primary/10 rounded-2xl flex items-center justify-center mx-auto">
                  <TrendingUp className="w-8 h-8 text-primary" />
                </div>
                <h3 className="text-xl font-semibold">3. Grow</h3>
                <p className="text-muted-foreground">
                  Follow your personalized roadmap with curated resources and AI-powered assessments featuring real-time validation.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 bg-gradient-to-r from-primary to-accent">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-3 gap-8 text-center text-white">
            <div className="space-y-2">
              <div className="text-4xl font-bold">1,000+</div>
              <div className="text-xl opacity-90">Careers Guided</div>
            </div>
            <div className="space-y-2">
              <div className="text-4xl font-bold">5+</div>
              <div className="text-xl opacity-90">Countries Served</div>
            </div>
            <div className="space-y-2">
              <div className="text-4xl font-bold">95%</div>
              <div className="text-xl opacity-90">Success Rate</div>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="testimonials" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center space-y-4 mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-foreground">
              What Our Users Say
            </h2>
            <p className="text-xl text-muted-foreground">
              Trusted by learners and professionals worldwide
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                name: "Sarah Chen",
                role: "Data Scientist",
                content:
                  "The AI guidance helped me transition from marketing to data science in just 8 months!",
                rating: 5,
              },
              {
                name: "Michael Rodriguez",
                role: "Product Manager",
                content:
                  "Incredible personalized roadmap. I landed my dream job at a Fortune 500 company.",
                rating: 5,
              },
              {
                name: "Priya Patel",
                role: "UX Designer",
                content:
                  "The learning resources were perfectly curated for my specific career goals.",
                rating: 5,
              },
            ].map((testimonial, index) => (
              <Card key={index} className="p-6">
                <CardContent className="space-y-4">
                  <div className="flex space-x-1">
                    {Array.from({ length: testimonial.rating }).map((_, i) => (
                      <Star
                        key={i}
                        className="w-5 h-5 fill-yellow-400 text-yellow-400"
                      />
                    ))}
                  </div>
                  <p className="text-muted-foreground italic">
                    "{testimonial.content}"
                  </p>
                  <div>
                    <div className="font-semibold">{testimonial.name}</div>
                    <div className="text-sm text-muted-foreground">
                      {testimonial.role}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-br from-primary/5 via-accent/5 to-background">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <div className="space-y-8">
            <h2 className="text-3xl lg:text-4xl font-bold text-foreground">
              Ready to Shape Your Future?
            </h2>
            <p className="text-xl text-muted-foreground">
              Join thousands of professionals who have transformed their careers
              with AI guidance
            </p>
            <Button
              size="lg"
              className="bg-primary hover:bg-primary/90"
              onClick={() => onNavigate("registration")}
            >
              Start Your Journey <ArrowRight className="ml-2 w-5 h-5" />
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t bg-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-2 gap-8">
            <div className="space-y-4">
              <div className="flex items-center space-x-2 justify-content-center justify-content-md-start">
                <div className="flex items-center justify-center">
                  <ImageWithFallback
                    src="assets/logo.svg"
                    alt="Anblicks AI Career Coaching"
                  />
                </div>
                <span className="text-xl font-semibold">
                  Anblicks Career Coach
                </span>
              </div>
            </div>
            <div className="space-y-4">
              <p className="text-muted-foreground text-center text-md-start">
                Empowering careers through AI-driven guidance and personalized
                learning paths.
              </p>
            </div>
          </div>
          <div className="border-t mt-8 pt-8 text-center text-muted-foreground">
            <p>
              &copy; {new Date().getFullYear()} Anblicks Career Coach. All
              rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

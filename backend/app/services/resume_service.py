from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional, BinaryIO
import uuid
from datetime import datetime
import json
import re
import google.generativeai as genai

from app.models.resume import Resume
from app.core.exceptions import NotFoundException, BadRequestException
from app.config import settings

# Configure Gemini
try:
    genai.configure(api_key=settings.GOOGLE_API_KEY)
    print("✅ Gemini API configured successfully")
    print(f"🔑 API Key starts with: {settings.GOOGLE_API_KEY[:10]}...")
except Exception as e:
    print(f"❌ Failed to configure Gemini API: {e}")
    raise


class ResumeService:

    @staticmethod
    def parse_resume_text(file_content: str) -> Dict[str, Any]:
        """
        Parse resume text and extract structured information using AI
        """

        model = genai.GenerativeModel('gemini-2.5-flash')

        prompt = f"""Analyze this resume and extract structured information.

Resume Content:
{file_content[:10000]}  # Limit to avoid token limits

Extract the following information and return as JSON:
{{
    "contact_info": {{
        "name": "Full Name",
        "email": "email@example.com",
        "phone": "+1234567890",
        "location": "City, Country",
        "linkedin": "linkedin.com/in/username",
        "github": "github.com/username",
        "portfolio": "website.com"
    }},
    "summary": "Professional summary or objective",
    "skills": ["skill1", "skill2", "skill3"],
    "experience": [
        {{
            "title": "Job Title",
            "company": "Company Name",
            "location": "City, Country",
            "start_date": "Jan 2020",
            "end_date": "Dec 2021",
            "description": "Job description",
            "achievements": ["achievement1", "achievement2"]
        }}
    ],
    "education": [
        {{
            "degree": "Bachelor of Science",
            "major": "Computer Science",
            "university": "University Name",
            "location": "City, Country",
            "graduation_date": "2020",
            "gpa": "3.8/4.0"
        }}
    ],
    "certifications": ["certification1", "certification2"],
    "projects": [
        {{
            "name": "Project Name",
            "description": "Project description",
            "technologies": ["tech1", "tech2"],
            "url": "github.com/project"
        }}
    ],
    "achievements": ["achievement1", "achievement2"],
    "languages": ["English", "Spanish"]
}}

Return ONLY valid JSON, no markdown or explanation."""

        try:
            response = model.generate_content(prompt)
            content = response.text.strip()

            # Clean markdown
            if content.startswith("```"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            parsed_data = json.loads(content)

            # Ensure all required fields exist
            default_structure = {
                "contact_info": {},
                "summary": "",
                "skills": [],
                "experience": [],
                "education": [],
                "certifications": [],
                "projects": [],
                "achievements": [],
                "languages": []
            }

            for key, default_value in default_structure.items():
                if key not in parsed_data:
                    parsed_data[key] = default_value

            return parsed_data

        except Exception as e:
            print(f"Resume parsing error: {e}")
            # Return basic structure with extracted text
            return {
                "contact_info": ResumeService._extract_contact_info(file_content),
                "summary": "",
                "skills": ResumeService._extract_skills(file_content),
                "experience": [],
                "education": [],
                "certifications": [],
                "projects": [],
                "achievements": [],
                "languages": []
            }

    @staticmethod
    def _extract_contact_info(text: str) -> Dict[str, str]:
        """Fallback: Extract contact info using regex"""
        contact_info = {}

        # Email
        email_match = re.search(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        if email_match:
            contact_info["email"] = email_match.group()

        # Phone
        phone_match = re.search(r'[\+$$]?[1-9][0-9 .\-$$$$]{8,}[0-9]', text)
        if phone_match:
            contact_info["phone"] = phone_match.group()

        # LinkedIn
        linkedin_match = re.search(
            r'linkedin\.com/in/[\w-]+', text, re.IGNORECASE)
        if linkedin_match:
            contact_info["linkedin"] = linkedin_match.group()

        # GitHub
        github_match = re.search(r'github\.com/[\w-]+', text, re.IGNORECASE)
        if github_match:
            contact_info["github"] = github_match.group()

        return contact_info

    @staticmethod
    def _extract_skills(text: str) -> List[str]:
        """Fallback: Extract common skills"""
        common_skills = [
            'Python', 'JavaScript', 'Java', 'C++', 'SQL', 'React', 'Node.js',
            'Django', 'Flask', 'FastAPI', 'MongoDB', 'PostgreSQL', 'AWS',
            'Docker', 'Kubernetes', 'Git', 'Machine Learning', 'AI', 'API'
        ]

        found_skills = []
        text_lower = text.lower()

        for skill in common_skills:
            if skill.lower() in text_lower:
                found_skills.append(skill)

        return found_skills

    @staticmethod
    def analyze_resume(parsed_data: Dict[str, Any], target_role: Optional[str] = None, raw_text: Optional[str] = None) -> Dict[str, Any]:
        """
        AI-powered comprehensive resume analysis using Gemini
        Provides detailed feedback on ATS compatibility, content quality, and improvements
        """

        # Configure safety settings to be more permissive for resume content
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            }
        ]

        model = genai.GenerativeModel(
            'gemini-2.5-flash',
            safety_settings=safety_settings
        )

        target_context = f"\nTarget Role: {target_role}" if target_role else "\nTarget Role: General Software Engineering"

        # Use raw text if available (better for AI analysis), otherwise use parsed data
        if raw_text:
            # Limit raw text to prevent timeouts (keep first 4000 chars - reduced for speed)
            resume_content = raw_text[:4000] if len(
                raw_text) > 4000 else raw_text
            content_label = "Resume Text"
            print(
                f"📝 Using raw text ({len(resume_content)} chars) for AI analysis")
        else:
            # Fallback to parsed data
            resume_content = json.dumps(parsed_data, indent=2)
            if len(resume_content) > 3000:
                resume_content = resume_content[:3000] + "\n... (truncated)"
            content_label = "Resume Data"
            print(
                f"📊 Using parsed data ({len(resume_content)} chars) for AI analysis")

        prompt = f"""You are an expert ATS analyzer. Analyze this resume and provide a fair, realistic assessment.

{content_label}:
{resume_content}
{target_context}

SCORING GUIDE (BE REALISTIC):
- 80-100: Excellent (strong experience, skills, achievements)
- 60-79: Good (solid content, room for improvement)
- 40-59: Average (needs work)
- 0-39: Poor (major gaps)

Most good resumes score 65-85. Don't penalize too harshly.

Return ONLY valid JSON in this EXACT format:

{{
    "ats_score": <integer 0-100, BE FAIR - most good resumes should score 65-85>,
    "overall_rating": "<excellent|good|average|needs_improvement>",

    "strengths": ["strength 1", "strength 2", "strength 3", "strength 4"],
    "weaknesses": ["weakness 1", "weakness 2", "weakness 3"],
    "suggestions": ["suggestion 1", "suggestion 2", "suggestion 3", "suggestion 4"],
    "keywords": ["keyword1", "keyword2", "keyword3"],
    "missing_sections": ["missing section if any"],

    "skills_analysis": {{
        "technical_skills": ["skill1", "skill2"],
        "soft_skills": ["soft skill1"],
        "missing_skills": ["missing skill1"],
        "skill_level": "junior|mid|senior",
        "skill_strength": "strong|moderate|weak"
    }},
    "experience_analysis": {{
        "total_years": 0,
        "relevant_experience": true,
        "career_progression": "good",
        "has_quantifiable_results": false,
        "gaps": [],
        "impact_score": "medium"
    }},
    "education_analysis": {{
        "relevance": "medium",
        "completeness": true,
        "recommendations": ["rec1"],
        "needs_improvement": false
    }},
    "content_quality": {{
        "has_action_verbs": true,
        "has_quantifiable_achievements": false,
        "formatting_score": 70,
        "readability": "good",
        "keyword_density": "medium"
    }},
    "recommendations": ["rec 1", "rec 2", "rec 3", "rec 4"],
    "keyword_match": {{
        "matched_keywords": ["keyword1"],
        "missing_keywords": ["keyword2"],
        "match_percentage": 50
    }},
    "detailed_feedback": "2-3 paragraph summary of the resume analysis"
}}

IMPORTANT: Return ONLY the JSON object above. No markdown, no code blocks, just pure JSON."""

        try:
            print("🤖 Sending resume to Gemini AI for analysis...")
            print(f"📄 Resume has {len(str(parsed_data))} characters")
            print(f"📝 Prompt length: {len(prompt)} characters")

            # Configure generation settings - optimized for quality and completeness
            generation_config = {
                "temperature": 0.4,  # Slightly higher for better quality
                "top_p": 0.9,
                "top_k": 20,
                "max_output_tokens": 8192,  # Maximum allowed - ensures complete responses
                "candidate_count": 1,  # Only one response
            }

            import time
            start_time = time.time()

            print("⏳ Waiting for AI analysis (may take up to 90 seconds)...")

            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )

            elapsed = time.time() - start_time
            print(f"⏱️ API call completed in {elapsed:.2f} seconds")

            if elapsed > 60:
                print(
                    "⚠️ Response took longer than expected, but completed successfully")

            # Check if response was blocked or empty
            if not response:
                print("❌ Gemini response was empty")
                return ResumeService._get_fallback_analysis(parsed_data)

            # Check finish reason early to warn about truncation
            if hasattr(response, 'candidates') and response.candidates:
                for candidate in response.candidates:
                    if hasattr(candidate, 'finish_reason'):
                        if candidate.finish_reason == 2:
                            print("⚠️ WARNING: Response was truncated (MAX_TOKENS)!")
                            print("⚠️ The JSON may be incomplete and require repair")

            # Handle multi-part responses properly
            try:
                content = response.text.strip()
                print(f"✅ Direct text access successful")
            except (ValueError, AttributeError) as e:
                # Handle multi-part responses or blocked responses
                print(f"⚠️ Cannot access response.text: {e}")
                print(f"🔍 Checking response structure...")

                # Check if response was blocked by safety filters
                if hasattr(response, 'prompt_feedback'):
                    print(f"📋 Prompt feedback: {response.prompt_feedback}")

                # Try to extract from candidates
                content = ""
                try:
                    if hasattr(response, 'candidates') and response.candidates:
                        print(
                            f"📦 Found {len(response.candidates)} candidate(s)")
                        for idx, candidate in enumerate(response.candidates):
                            print(
                                f"  Candidate {idx}: {type(candidate)}, has_content={hasattr(candidate, 'content')}")

                            if hasattr(candidate, 'content'):
                                content_obj = candidate.content
                                print(
                                    f"  Content: {type(content_obj)}, has_parts={hasattr(content_obj, 'parts')}")

                                if content_obj and hasattr(content_obj, 'parts'):
                                    parts_list = content_obj.parts
                                    print(
                                        f"  Parts list type: {type(parts_list)}")
                                    print(
                                        f"  Parts list value: {parts_list}")
                                    print(
                                        f"  Parts: {len(parts_list) if parts_list else 0} part(s)")

                                    # Also try to access as list
                                    try:
                                        parts_as_list = list(parts_list)
                                        print(
                                            f"  Parts as list: {len(parts_as_list)} items")
                                        if parts_as_list:
                                            for part_idx, part in enumerate(parts_as_list):
                                                print(
                                                    f"    Part {part_idx}: {type(part)}")
                                                # Try to get text
                                                if hasattr(part, 'text'):
                                                    text_val = part.text
                                                    if text_val:
                                                        content += str(text_val)
                                                        print(
                                                            f"    ✅ Extracted {len(text_val)} chars")
                                                else:
                                                    print(
                                                        f"    ❌ No text attribute, attrs: {[a for a in dir(part) if not a.startswith('_')][:5]}")
                                    except Exception as list_error:
                                        print(
                                            f"  ❌ Error converting to list: {list_error}")

                                    # Also check candidate's role and finish_reason
                                    if hasattr(candidate, 'finish_reason'):
                                        finish_reason = candidate.finish_reason
                                        reason_map = {
                                            0: "UNSPECIFIED",
                                            1: "STOP (normal)",
                                            2: "MAX_TOKENS (truncated!)",
                                            3: "SAFETY (blocked)",
                                            4: "RECITATION",
                                            5: "OTHER"
                                        }
                                        reason_name = reason_map.get(
                                            finish_reason, f"Unknown({finish_reason})")
                                        print(
                                            f"  Finish reason: {reason_name}")

                                        if finish_reason == 2:
                                            print(
                                                "  ⚠️ Response was truncated due to MAX_TOKENS!")
                                            print(
                                                "  This means we need more output tokens or shorter prompt")

                                    if hasattr(candidate, 'safety_ratings'):
                                        print(
                                            f"  Safety ratings: {candidate.safety_ratings}")

                    if not content and hasattr(response, 'parts') and response.parts:
                        # Fallback to direct parts access
                        print(
                            f"🔄 Trying direct parts ({len(response.parts)} parts)")
                        for idx, part in enumerate(response.parts):
                            if hasattr(part, 'text') and part.text:
                                text_len = len(part.text)
                                content += part.text
                                print(f"✅ Direct part {idx}: {text_len} chars")

                    content = content.strip()
                except Exception as part_error:
                    print(
                        f"❌ Failed to extract: {part_error}")
                    import traceback
                    traceback.print_exc()
                    return ResumeService._get_fallback_analysis(parsed_data)

            if not content:
                print("❌ No text content after extraction")
                return ResumeService._get_fallback_analysis(parsed_data)

            print(f"✅ Received AI response ({len(content)} chars), parsing...")

            # Clean markdown formatting and extract JSON
            print(f"📦 Raw content length: {len(content)} chars")

            # Remove markdown code blocks
            if content.startswith("```json"):
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            # Try to extract JSON if there's other text
            if not content.startswith('{'):
                # Find first { and extract from there
                json_start = content.find('{')
                if json_start != -1:
                    content = content[json_start:]
                    print(f"🔧 Extracted JSON from position {json_start}")

            if not content.endswith('}'):
                # Find last } and extract until there
                json_end = content.rfind('}')
                if json_end != -1:
                    content = content[:json_end+1]
                    print(
                        f"🔧 Truncated to last closing brace at position {json_end}")

            print(f"🔍 Cleaned content preview: {content[:200]}...")
            print(f"📏 Final content length: {len(content)} chars")

            # Try to parse JSON, with advanced repair if needed
            try:
                analysis = json.loads(content)
                print("✅ AI analysis parsed successfully")
            except json.JSONDecodeError as parse_error:
                print(f"⚠️ Initial JSON parse failed: {parse_error}")
                print(f"⚠️ Error at char {parse_error.pos}: {parse_error.msg}")
                print("🔧 Attempting to repair JSON...")

                repaired_content = content

                # Strategy 1: Fix unterminated strings
                if "Unterminated string" in str(parse_error):
                    # Find the error position and close the string
                    error_pos = parse_error.pos
                    if error_pos < len(content):
                        # Truncate at error and add closing quote
                        repaired_content = content[:error_pos] + '"'
                        print(
                            f"🔧 Closed unterminated string at pos {error_pos}")

                # Strategy 2: Balance braces and brackets
                open_braces = repaired_content.count('{')
                close_braces = repaired_content.count('}')
                open_brackets = repaired_content.count('[')
                close_brackets = repaired_content.count(']')

                print(f"🔧 Braces: {open_braces} open, {close_braces} close")
                print(
                    f"🔧 Brackets: {open_brackets} open, {close_brackets} close")

                # Close any open strings first
                if repaired_content.count('"') % 2 != 0:
                    repaired_content += '"'
                    print("🔧 Closed unterminated quote")

                # Close arrays first, then objects
                while open_brackets > close_brackets:
                    repaired_content += ']'
                    close_brackets += 1
                    print("🔧 Added closing bracket ]")

                while open_braces > close_braces:
                    repaired_content += '}'
                    close_braces += 1
                    print("🔧 Added closing brace }")

                print(f"🔧 Repair complete, trying parse...")

                try:
                    analysis = json.loads(repaired_content)
                    print("✅ Successfully parsed repaired JSON!")
                except json.JSONDecodeError as repair_error:
                    print(f"❌ Repair failed: {repair_error}")
                    print(
                        f"❌ Repaired content (last 300 chars): ...{repaired_content[-300:]}")
                    raise parse_error  # Re-raise original error

            # Ensure all required fields exist with defaults
            default_analysis = {
                "ats_score": ResumeService._calculate_ats_score(parsed_data),
                "overall_rating": "average",
                "strengths": [],
                "weaknesses": [],
                "suggestions": [],
                "keywords": [],
                "missing_sections": [],
                "skills_analysis": {
                    "technical_skills": [],
                    "soft_skills": [],
                    "missing_skills": [],
                    "skill_level": "mid",
                    "skill_strength": "moderate"
                },
                "experience_analysis": {
                    "total_years": 0,
                    "relevant_experience": True,
                    "career_progression": "average",
                    "has_quantifiable_results": False,
                    "gaps": [],
                    "impact_score": "medium"
                },
                "education_analysis": {
                    "relevance": "medium",
                    "completeness": True,
                    "recommendations": [],
                    "needs_improvement": False
                },
                "content_quality": {
                    "has_action_verbs": False,
                    "has_quantifiable_achievements": False,
                    "formatting_score": 70,
                    "readability": "good",
                    "keyword_density": "medium"
                },
                "recommendations": [],
                "keyword_match": {
                    "matched_keywords": [],
                    "missing_keywords": [],
                    "match_percentage": 50
                },
                "detailed_feedback": ""
            }

            # Merge AI analysis with defaults
            for key, value in default_analysis.items():
                if key not in analysis:
                    analysis[key] = value
                elif isinstance(value, dict):
                    # Merge nested dictionaries
                    for subkey, subvalue in value.items():
                        if subkey not in analysis[key]:
                            analysis[key][subkey] = subvalue

            # Ensure ATS score is valid integer and within range
            if "ats_score" in analysis:
                try:
                    ai_score = int(analysis["ats_score"])
                    # Trust AI score, just ensure it's in valid range
                    analysis["ats_score"] = max(0, min(100, ai_score))
                    print(f"📊 AI ATS Score: {analysis['ats_score']}/100")
                except:
                    # Only fallback if AI score is invalid
                    fallback_score = ResumeService._calculate_ats_score(
                        parsed_data)
                    analysis["ats_score"] = fallback_score
                    print(f"⚠️ Using fallback score: {fallback_score}/100")
            else:
                # AI didn't provide score, use fallback
                analysis["ats_score"] = ResumeService._calculate_ats_score(
                    parsed_data)
                print(
                    f"⚠️ No AI score, using fallback: {analysis['ats_score']}/100")

            return analysis

        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            print(f"❌ Failed content (first 1000 chars): {content[:1000]}")
            print("⚠️ Falling back to manual analysis")
            return ResumeService._get_fallback_analysis(parsed_data)

        except AttributeError as e:
            print(f"❌ Gemini API response error: {e}")
            print("⚠️ This usually means Gemini blocked the response or API key issue")
            import traceback
            traceback.print_exc()
            return ResumeService._get_fallback_analysis(parsed_data)

        except Exception as e:
            error_type = type(e).__name__

            # Handle timeout errors - retry once with patience
            if "DeadlineExceeded" in error_type or "Timeout" in error_type:
                print(f"⏱️ Request timed out, retrying with extended wait...")
                print(f"⏳ Please wait up to 90 seconds for complete AI analysis...")

                try:
                    # Retry - Gemini will automatically use a longer timeout
                    import time
                    retry_start = time.time()

                    retry_response = model.generate_content(
                        prompt,
                        generation_config=generation_config
                    )

                    retry_elapsed = time.time() - retry_start
                    print(f"⏱️ Retry completed in {retry_elapsed:.2f} seconds")

                    if retry_response:
                        try:
                            retry_content = retry_response.text.strip()
                            # Clean markdown
                            if retry_content.startswith("```json"):
                                retry_content = retry_content[7:]
                            elif retry_content.startswith("```"):
                                retry_content = retry_content[3:]
                            if retry_content.endswith("```"):
                                retry_content = retry_content[:-3]
                            retry_content = retry_content.strip()

                            retry_analysis = json.loads(retry_content)
                            print(
                                f"✅ Retry successful! ATS Score: {retry_analysis.get('ats_score', 0)}/100")

                            # Merge with defaults
                            fallback = ResumeService._get_fallback_analysis(
                                parsed_data)
                            for key, value in fallback.items():
                                if key not in retry_analysis:
                                    retry_analysis[key] = value

                            return retry_analysis
                        except Exception as retry_parse_error:
                            print(
                                f"⚠️ Retry parse failed: {retry_parse_error}")

                    print("⚠️ Retry response invalid, using fallback")
                    return ResumeService._get_fallback_analysis(parsed_data)

                except Exception as retry_error:
                    print(f"⚠️ Retry also failed: {retry_error}")
                    print("⚠️ Using enhanced fallback analysis")
                    return ResumeService._get_fallback_analysis(parsed_data)

            print(f"❌ Unexpected analysis error: {error_type}: {e}")
            import traceback
            traceback.print_exc()
            print("⚠️ Falling back to manual analysis")
            return ResumeService._get_fallback_analysis(parsed_data)

    @staticmethod
    def _get_fallback_analysis(parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate enhanced fallback analysis when AI fails"""
        print("📊 Generating enhanced fallback analysis...")

        # Calculate basic ATS score with more generous, realistic scoring
        base_score = ResumeService._calculate_ats_score(parsed_data)

        # Enhance the score to be more realistic
        # Good resumes should score 65-80, excellent ones 80-95
        num_skills = len(parsed_data.get('skills', []))
        num_experience = len(parsed_data.get('experience', []))
        has_education = bool(parsed_data.get('education'))
        has_contact = bool(parsed_data.get('contact_info'))

        # Start with boosted base score
        ats_score = min(95, int(base_score * 2.2))  # Boost by 120%

        # Add bonuses for good content
        if num_skills >= 10:
            ats_score += 5
        if num_experience >= 2:
            ats_score += 5
        if has_education:
            ats_score += 3
        if has_contact:
            ats_score += 3

        # Ensure reasonable range
        if ats_score < 55 and (num_skills > 0 or num_experience > 0):
            ats_score = 55 + (num_skills * 2) + (num_experience * 3)

        ats_score = min(95, max(50, ats_score))  # Cap between 50-95

        print(
            f"✅ Fallback ATS Score: {ats_score}/100 (base: {base_score}, skills: {num_skills}, exp: {num_experience})")

        return {
            "ats_score": ats_score,
            "overall_rating": "good" if ats_score >= 70 else "average" if ats_score >= 50 else "needs_improvement",
            "strengths": [
                "Resume structure includes essential sections",
                f"Contact information is {'complete' if parsed_data.get('contact_info') else 'present'}",
                f"Skills section contains {len(parsed_data.get('skills', []))} skills",
                f"Experience section includes {len(parsed_data.get('experience', []))} positions"
            ],
            "weaknesses": [
                "Unable to perform detailed AI analysis at this time",
                "Manual review recommended for comprehensive feedback",
                "Consider adding more quantifiable achievements"
            ],
            "suggestions": [
                "Add specific metrics and numbers to achievements (e.g., 'Increased sales by 30%')",
                "Use strong action verbs (e.g., 'Led', 'Developed', 'Implemented')",
                "Ensure all sections are complete and up-to-date",
                "Tailor resume content to match target role keywords",
                "Include links to portfolio, GitHub, or LinkedIn profile"
            ],
            "keywords": parsed_data.get("skills", [])[:15],
            "missing_sections": [],
            "skills_analysis": {
                "technical_skills": parsed_data.get("skills", []),
                "soft_skills": ["Communication", "Problem Solving", "Teamwork"],
                "missing_skills": ["Add role-specific technical skills"],
                "skill_level": "mid",
                "skill_strength": "moderate"
            },
            "experience_analysis": {
                "total_years": len(parsed_data.get("experience", [])),
                "relevant_experience": True,
                "career_progression": "average",
                "has_quantifiable_results": False,
                "gaps": [],
                "impact_score": "medium"
            },
            "education_analysis": {
                "relevance": "medium",
                "completeness": bool(parsed_data.get("education")),
                "recommendations": ["Ensure education details are complete"],
                "needs_improvement": not bool(parsed_data.get("education"))
            },
            "content_quality": {
                "has_action_verbs": True,
                "has_quantifiable_achievements": False,
                "formatting_score": ats_score,
                "readability": "good",
                "keyword_density": "medium"
            },
            "recommendations": [
                "Quantify achievements with specific numbers and percentages",
                "Add more technical skills relevant to your target role",
                "Include links to your professional profiles and portfolio",
                "Ensure consistent formatting throughout the resume",
                "Add a professional summary highlighting key strengths"
            ],
            "keyword_match": {
                "matched_keywords": parsed_data.get("skills", [])[:10],
                "missing_keywords": ["Cloud Computing", "Agile", "CI/CD"],
                "match_percentage": min(ats_score, 75)
            },
            "detailed_feedback": f"""Your resume has an ATS compatibility score of {ats_score}/100. 
            
The resume includes the essential sections and demonstrates a {len(parsed_data.get('experience', []))} work experiences with {len(parsed_data.get('skills', []))} listed skills. To improve your ATS score and interview chances, focus on adding quantifiable achievements with specific metrics, using strong action verbs throughout, and ensuring all contact information is complete.

Key recommendations include tailoring your resume to match the specific job description, adding measurable results to your experience descriptions, and including relevant keywords for your target role. Consider adding a professional summary at the top and ensuring your technical skills section is comprehensive and up-to-date.

Your resume is on the right track, but implementing these improvements will significantly enhance its effectiveness in passing ATS screening and attracting recruiter attention."""
        }

    @staticmethod
    def _calculate_ats_score(parsed_data: Dict[str, Any]) -> int:
        """
        Advanced ATS score calculation based on multiple factors:
        - Contact Information Completeness
        - Skills Relevance and Quantity
        - Experience Quality and Quantity
        - Education Credentials
        - Additional Sections (Projects, Certifications, Achievements)
        - Content Quality (Keywords, Quantifiable Results)
        """
        score = 0

        # 1. Contact Information (15 points)
        contact = parsed_data.get("contact_info", {})
        contact_score = 0
        if contact.get("email"):
            contact_score += 4
        if contact.get("phone"):
            contact_score += 3
        if contact.get("name"):
            contact_score += 3
        if contact.get("linkedin"):
            contact_score += 3
        if contact.get("github") or contact.get("portfolio"):
            contact_score += 2
        score += min(15, contact_score)

        # 2. Professional Summary (10 points)
        summary = parsed_data.get("summary", "")
        if summary and len(summary.strip()) > 50:
            score += 10
        elif summary and len(summary.strip()) > 20:
            score += 5

        # 3. Skills Section (20 points)
        skills = parsed_data.get("skills", [])
        skill_count = len(skills)
        if skill_count >= 10:
            score += 20
        elif skill_count >= 7:
            score += 16
        elif skill_count >= 5:
            score += 12
        elif skill_count >= 3:
            score += 8
        elif skill_count >= 1:
            score += 4

        # 4. Work Experience (25 points)
        experience = parsed_data.get("experience", [])
        exp_score = 0

        # Points for number of positions
        exp_count = len(experience)
        if exp_count >= 4:
            exp_score += 12
        elif exp_count >= 3:
            exp_score += 10
        elif exp_count >= 2:
            exp_score += 7
        elif exp_count >= 1:
            exp_score += 5

        # Points for detailed achievements
        for exp in experience:
            if isinstance(exp, dict):
                achievements = exp.get("achievements", [])
                description = exp.get("description", "")

                # Check for quantifiable results (numbers, percentages)
                if achievements and len(achievements) > 0:
                    exp_score += 2
                    # Bonus for quantifiable achievements
                    achievement_text = " ".join(achievements)
                    if any(char.isdigit() for char in achievement_text):
                        exp_score += 2

                # Check for action verbs in description
                if description:
                    action_verbs = ["developed", "built", "created", "managed", "led",
                                    "implemented", "designed", "improved", "increased", "reduced"]
                    if any(verb in description.lower() for verb in action_verbs):
                        exp_score += 1

        score += min(25, exp_score)

        # 5. Education (15 points)
        education = parsed_data.get("education", [])
        edu_score = 0

        if len(education) >= 1:
            edu_score += 10

            # Bonus for degree details
            for edu in education:
                if isinstance(edu, dict):
                    if edu.get("degree"):
                        edu_score += 2
                    if edu.get("gpa") or edu.get("graduation_date"):
                        edu_score += 1
                    break  # Only check first education entry for details

        score += min(15, edu_score)

        # 6. Projects (10 points)
        projects = parsed_data.get("projects", [])
        project_score = 0

        if len(projects) >= 3:
            project_score += 8
        elif len(projects) >= 2:
            project_score += 6
        elif len(projects) >= 1:
            project_score += 4

        # Bonus for project details
        for proj in projects:
            if isinstance(proj, dict):
                if proj.get("technologies") and len(proj.get("technologies", [])) > 0:
                    project_score += 1
                if proj.get("url") or proj.get("github"):
                    project_score += 1

        score += min(10, project_score)

        # 7. Certifications (5 points)
        certifications = parsed_data.get("certifications", [])
        if len(certifications) >= 3:
            score += 5
        elif len(certifications) >= 2:
            score += 4
        elif len(certifications) >= 1:
            score += 3

        # 8. Additional Sections (5 points)
        additional_score = 0

        achievements = parsed_data.get("achievements", [])
        if achievements and len(achievements) > 0:
            additional_score += 2

        languages = parsed_data.get("languages", [])
        if languages and len(languages) >= 2:
            additional_score += 2
        elif languages and len(languages) >= 1:
            additional_score += 1

        score += min(5, additional_score)

        # Ensure score is between 0 and 100
        return max(0, min(100, score))

    @staticmethod
    def get_resume(db: Session, resume_id: uuid.UUID, user_id: uuid.UUID) -> Resume:
        """Get resume by ID"""
        resume = db.query(Resume).filter(
            Resume.id == resume_id,
            Resume.user_id == user_id
        ).first()

        if not resume:
            raise NotFoundException("Resume not found")

        return resume

    @staticmethod
    def get_user_resumes(db: Session, user_id: uuid.UUID) -> List[Resume]:
        """Get all resumes for a user"""
        return db.query(Resume).filter(
            Resume.user_id == user_id
        ).order_by(Resume.created_at.desc()).all()

    @staticmethod
    def set_primary_resume(db: Session, resume_id: uuid.UUID, user_id: uuid.UUID):
        """Set a resume as primary"""
        # Unset all primary resumes
        db.query(Resume).filter(Resume.user_id ==
                                user_id).update({"is_primary": False})

        # Set new primary
        resume = ResumeService.get_resume(db, resume_id, user_id)
        resume.is_primary = True
        db.commit()

    @staticmethod
    def delete_resume(db: Session, resume_id: uuid.UUID, user_id: uuid.UUID):
        """Delete a resume"""
        resume = ResumeService.get_resume(db, resume_id, user_id)

        # TODO: Delete file from Supabase storage

        db.delete(resume)
        db.commit()

import unittest
import sys
from pathlib import Path

# Add ingest directory to sys.path
INGEST_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(INGEST_DIR))

from server import smart_streamline_narrative


class TestNarrativeStreamline(unittest.TestCase):

    def setUp(self):
        self.sample_raw_transcript = (
            "Welcome to the deep dive. Today we are looking at Meta Muse. Right. "
            "Imagine waking up tomorrow, you know, grabbing your phone, checking WhatsApp. "
            "You see a message from, well, a digital intern, right? Like an actual assistant. Yeah. "
            "Exactly. And it casually informs you that while you were sleeping, it harvested your tax losses. "
            "All in the background. Right. It didn't give you advice on how to do these things. "
            "It just did them. Exactly. "
            "Meta Muse was developed within Meta Superintelligence Labs. Right. "
            "Muse drives a headless browser and parses the DOM. Precisely. "
            "If you want to secure enclave of your own to read this Meta Muse strategic analysis for yourself, "
            "you can go to our research hub at deepdive website. You can now access all of the research offline. "
            "The deep dive website is now a progressive web app. What that means is you can install it essentially as a native app. "
            "So getting back to the competitive landscape of the AI industry. "
            "Apple is structurally incapable of hosting persistent asynchronous agents right now. Correct. "
            "And it's exactly why you, the listener, should share this show. "
            "As we draw this deep dive to a close, I want to offer a synthesis. "
            "The internet was built for human eyes, but the next iteration may be built exclusively for agentic code. "
            "Once again, we want to request that you subscribe to the show on your platform of choice. "
            "Keep searching, keep the quest on, see you on the next deep dive. I am Satoshi."
        )

    def test_no_podcast_metadata_header_or_footer(self):
        """Verifies that podcast headers, NIP-23 badges, and Lightning tip footers are NOT injected."""
        output, _ = smart_streamline_narrative(
            self.sample_raw_transcript,
            title="MetaMuse Architecture",
            ep_num="247",
            lightning_addr="shutosha@primal.net"
        )
        # Should not contain podcast metadata headers
        self.assertNotIn("DeepDive Audio Intelligence", output)
        self.assertNotIn("Nostr Long-Form Publication", output)
        self.assertNotIn("NIP-23", output)

        # Should not contain crypto / sats footer
        self.assertNotIn("Connect & Support", output)
        self.assertNotIn("Lightning Tips", output)
        self.assertNotIn("shutosha@primal.net", output)
        self.assertNotIn("Generated via MD² Ingest Studio", output)

        # Must retain clean H1
        self.assertTrue(output.startswith("# **MetaMuse** Architecture") or output.startswith("# MetaMuse Architecture"))

    def test_single_word_interjections_eliminated(self):
        """Verifies that standalone interjections ('Right.', 'Exactly.', 'Yeah.', etc.) are removed."""
        output, _ = smart_streamline_narrative(self.sample_raw_transcript, title="Test")

        # Test standalone words with punctuation
        bad_interjections = [
            " Right.", " Right?", " Right!", " Exactly.", " Precisely.",
            " Correct.", " Yeah.", " Yep.", " Yes.", " Okay.", " Wow."
        ]
        for interjection in bad_interjections:
            self.assertNotIn(f"\n{interjection.strip()} ", output)
            self.assertNotIn(f" {interjection.strip()} ", output)

        # Test trailing tag question elimination
        self.assertNotIn("intern, right?", output)
        self.assertNotIn("intern, right.", output)
        self.assertIn("intern. Like an actual assistant.", output)

    def test_ruthless_promotion_and_meta_removal(self):
        """Verifies that show promotions, offline app pitches, and signoffs are completely dropped."""
        output, _ = smart_streamline_narrative(self.sample_raw_transcript, title="Test")

        # Must not contain show promos or meta talk
        self.assertNotIn("Welcome to the deep dive", output)
        self.assertNotIn("deep dive website", output)
        self.assertNotIn("progressive web app", output)
        self.assertNotIn("install it essentially as a native app", output)
        self.assertNotIn("access all of the research offline", output)
        self.assertNotIn("share this show", output)
        self.assertNotIn("subscribe to the show", output)
        self.assertNotIn("As we draw this deep dive to a close", output)
        self.assertNotIn("see you on the next deep dive", output)
        self.assertNotIn("I am Satoshi", output)
        self.assertNotIn("Promotional Note", output)

    def test_substantive_content_and_entities_preserved(self):
        """Verifies technical concepts are preserved and key entities bolded."""
        output, _ = smart_streamline_narrative(self.sample_raw_transcript, title="Test")

        self.assertIn("**Meta Superintelligence Labs**", output)
        self.assertIn("**headless browser**", output)
        self.assertIn("**DOM**", output)
        self.assertIn("The internet was built for human eyes, but the next iteration may be built exclusively for agentic code.", output)


if __name__ == '__main__':
    unittest.main()
